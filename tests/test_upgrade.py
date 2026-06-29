"""Upgrade: refresh kit-managed files (incl. AGENTS.md core region), keep project."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agentkit import init as init_mod, presets, validate as validate_mod


class UpgradeTests(unittest.TestCase):
    def test_upgrade_refreshes_managed_context_and_preserves_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)

            # drift: corrupt a kit-managed source file
            (root / ".agents/README.md").write_text("BROKEN\n", encoding="utf-8")

            # tamper the AGENTS.md core region; add real content to the project region
            agents = root / "AGENTS.md"
            txt = agents.read_text(encoding="utf-8")
            txt = txt.replace("## Canonical Agent Context",
                              "## Canonical Agent Context\nTAMPERED-CORE")
            txt = txt.replace("_Add project-specific guidance here",
                              "MY PROJECT NOTES keep me")
            agents.write_text(txt, encoding="utf-8")

            updated = init_mod.upgrade(root)

            readme = (root / ".agents/README.md").read_text(encoding="utf-8")
            self.assertNotIn("BROKEN", readme)
            self.assertIn("Skill Taxonomy and Naming", readme)

            new_agents = agents.read_text(encoding="utf-8")
            self.assertNotIn("TAMPERED-CORE", new_agents)          # core region refreshed
            self.assertIn("MY PROJECT NOTES keep me", new_agents)  # project region preserved
            self.assertIn("AGENTS.md (core region)", updated)

            self.assertEqual(validate_mod.validate(root), [])

    def test_upgrade_refresh_presets_restores_preset_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)
            presets.apply_preset(root, presets.resolve_preset("preset-spring-boot"))

            skill = root / ".agents/skills/stack-springboot/SKILL.md"
            skill.write_text("BROKEN\n", encoding="utf-8")  # drift a preset skill

            init_mod.upgrade(root, refresh_presets=True)

            restored = skill.read_text(encoding="utf-8")
            self.assertNotIn("BROKEN", restored)
            self.assertIn("stack-springboot", restored)
            self.assertEqual(validate_mod.validate(root), [])


if __name__ == "__main__":
    unittest.main()
