"""Preset apply: applying a preset keeps the project valid and in sync."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agentkit import generate_adapters, init as init_mod, presets, validate as validate_mod


class PresetApplyTests(unittest.TestCase):
    def test_apply_preset_base_stays_valid_and_in_sync(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)

            pdir = presets.resolve_preset("preset-base")
            self.assertIsNotNone(pdir)
            applied = presets.apply_preset(root, pdir)
            self.assertTrue(any(a.startswith("skill:virtual-assistant-") for a in applied))

            # VA skills vendored and recorded
            self.assertTrue((root / ".agents/skills/virtual-assistant-developer/SKILL.md").exists())
            proj = json.loads((root / ".agents/project.json").read_text())
            self.assertIn("virtual-assistant-developer", proj["skills"]["virtual-assistant"])
            self.assertIn({"name": "preset-base", "version": "0.1.0"}, proj["kit"]["presets"])

            # regenerate and verify everything stays consistent
            generate_adapters.sync(root, check=False)
            self.assertEqual(generate_adapters.sync(root, check=True), [])
            self.assertEqual(validate_mod.validate(root), [])

    def test_apply_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)
            pdir = presets.resolve_preset("preset-base")
            presets.apply_preset(root, pdir)
            presets.apply_preset(root, pdir)  # second apply: no errors, still in sync
            generate_adapters.sync(root, check=False)
            self.assertEqual(generate_adapters.sync(root, check=True), [])
            proj = json.loads((root / ".agents/project.json").read_text())
            # preset recorded once
            self.assertEqual(
                [p for p in proj["kit"]["presets"] if p["name"] == "preset-base"],
                [{"name": "preset-base", "version": "0.1.0"}],
            )

    def test_resolve_unknown_preset_is_none(self):
        self.assertIsNone(presets.resolve_preset("preset-does-not-exist"))


if __name__ == "__main__":
    unittest.main()
