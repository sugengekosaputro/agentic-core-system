"""Preset apply: applying a preset keeps the project valid and in sync."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agentkit import generate_adapters, init as init_mod, presets, validate as validate_mod


class PresetApplyTests(unittest.TestCase):
    def test_preset_base_is_removed(self):
        self.assertNotIn("preset-base", presets.available_presets())
        self.assertIsNone(presets.resolve_preset("preset-base"))

    def test_apply_stack_preset_stays_valid_and_in_sync(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)

            pdir = presets.resolve_preset("preset-angular")
            self.assertIsNotNone(pdir)
            applied = presets.apply_preset(root, pdir)
            self.assertIn("skill:stack-angular", applied)

            # stack skill vendored and recorded
            self.assertTrue((root / ".agents/skills/stack-angular/SKILL.md").exists())
            proj = json.loads((root / ".agents/project.json").read_text())
            self.assertIn("stack-angular", proj["skills"]["stack"])
            self.assertEqual(proj["skills"]["workflow"], [])
            self.assertIn({"name": "preset-angular", "version": "0.2.0"}, proj["kit"]["presets"])

            # regenerate and verify everything stays consistent
            generate_adapters.sync(root, check=False)
            self.assertEqual(generate_adapters.sync(root, check=True), [])
            self.assertEqual(validate_mod.validate(root), [])

    def test_apply_workflow_standard_preset_records_workflow_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)

            pdir = presets.resolve_preset("preset-workflow-standard")
            self.assertIsNotNone(pdir)
            applied = presets.apply_preset(root, pdir)

            expected = [
                "workflow-explore",
                "workflow-implement",
                "workflow-plan",
                "workflow-review",
            ]
            for name in expected:
                self.assertIn(f"skill:{name}", applied)
                self.assertTrue((root / f".agents/skills/{name}/SKILL.md").exists())

            proj = json.loads((root / ".agents/project.json").read_text())
            self.assertEqual(sorted(proj["skills"]["workflow"]), sorted(expected))
            self.assertEqual(proj["skills"]["stack"], [])
            self.assertIn({"name": "preset-workflow-standard", "version": "0.2.0"}, proj["kit"]["presets"])

            generate_adapters.sync(root, check=False)
            self.assertEqual(generate_adapters.sync(root, check=True), [])
            self.assertEqual(validate_mod.validate(root), [])

    def test_apply_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)
            pdir = presets.resolve_preset("preset-angular")
            presets.apply_preset(root, pdir)
            presets.apply_preset(root, pdir)  # second apply: no errors, still in sync
            generate_adapters.sync(root, check=False)
            self.assertEqual(generate_adapters.sync(root, check=True), [])
            proj = json.loads((root / ".agents/project.json").read_text())
            # preset recorded once
            self.assertEqual(
                [p for p in proj["kit"]["presets"] if p["name"] == "preset-angular"],
                [{"name": "preset-angular", "version": "0.2.0"}],
            )

    def test_resolve_unknown_preset_is_none(self):
        self.assertIsNone(presets.resolve_preset("preset-does-not-exist"))


class StackPresetTests(unittest.TestCase):
    def test_each_stack_preset_applies_clean(self):
        stack_presets = [
            str(info["name"])
            for info in presets.available_preset_infos()
            if info.get("kind") == "stack"
        ]
        self.assertTrue(stack_presets, "expected at least one stack preset")
        for name in stack_presets:
            with self.subTest(preset=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                init_mod.run(root)
                presets.apply_preset(root, presets.resolve_preset(name))
                generate_adapters.sync(root, check=False)
                self.assertEqual(generate_adapters.sync(root, check=True), [])
                self.assertEqual(validate_mod.validate(root), [])
                # AGENTS.md must stay within the context budget after the project region grows
                self.assertLessEqual(len((root / "AGENTS.md").read_bytes()), 7000)
                # the preset's verify command is wired (drives the pre-push gate)
                proj = json.loads((root / ".agents/project.json").read_text())
                self.assertTrue(proj["commands"].get("verify"))

    def test_spring_boot_records_stack_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)
            presets.apply_preset(root, presets.resolve_preset("preset-spring-boot"))

            proj = json.loads((root / ".agents/project.json").read_text())
            self.assertIn("stack-springboot", proj["skills"]["stack"])
            self.assertIn("stack-database", proj["skills"]["stack"])


if __name__ == "__main__":
    unittest.main()
