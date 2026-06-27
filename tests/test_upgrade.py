"""Upgrade: refresh kit-managed files (incl. AGENTS.md core region), keep project."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agentkit import init as init_mod, validate as validate_mod


class UpgradeTests(unittest.TestCase):
    def test_upgrade_restores_core_and_preserves_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)

            # drift: corrupt a core skill
            (root / ".agents/skills/core-init/SKILL.md").write_text("BROKEN\n", encoding="utf-8")

            # tamper the AGENTS.md core region; add real content to the project region
            agents = root / "AGENTS.md"
            txt = agents.read_text(encoding="utf-8")
            txt = txt.replace("## Canonical Agent Context",
                              "## Canonical Agent Context\nTAMPERED-CORE")
            txt = txt.replace("_Add project-specific guidance here",
                              "MY PROJECT NOTES keep me")
            agents.write_text(txt, encoding="utf-8")

            updated = init_mod.upgrade(root)

            skill = (root / ".agents/skills/core-init/SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("BROKEN", skill)
            self.assertIn("core-init", skill)

            new_agents = agents.read_text(encoding="utf-8")
            self.assertNotIn("TAMPERED-CORE", new_agents)          # core region refreshed
            self.assertIn("MY PROJECT NOTES keep me", new_agents)  # project region preserved
            self.assertIn("AGENTS.md (core region)", updated)

            self.assertEqual(validate_mod.validate(root), [])


if __name__ == "__main__":
    unittest.main()
