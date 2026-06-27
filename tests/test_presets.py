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


class StackPresetTests(unittest.TestCase):
    def test_each_stack_preset_applies_clean(self):
        stack_presets = [p for p in presets.available_presets() if p != "preset-base"]
        self.assertTrue(stack_presets, "expected at least one stack preset")
        for name in stack_presets:
            with self.subTest(preset=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                init_mod.run(root)
                presets.apply_preset(root, presets.resolve_preset("preset-base"))
                presets.apply_preset(root, presets.resolve_preset(name))
                generate_adapters.sync(root, check=False)
                self.assertEqual(generate_adapters.sync(root, check=True), [])
                self.assertEqual(validate_mod.validate(root), [])
                # AGENTS.md must stay within the context budget after the project region grows
                self.assertLessEqual(len((root / "AGENTS.md").read_bytes()), 7000)
                # the preset's verify command is wired (drives the pre-push gate)
                proj = json.loads((root / ".agents/project.json").read_text())
                self.assertTrue(proj["commands"].get("verify"))


if __name__ == "__main__":
    unittest.main()

