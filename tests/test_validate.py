"""Validation rules for the workflow/stack skill model."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agentkit import init as init_mod, validate as validate_mod


def _write_skill(root: Path, name: str) -> None:
    path = root / ".agents/skills" / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "---",
                f"name: {name}",
                "description: test skill",
                "---",
                "",
                "# Test",
                "",
            ]
        ),
        encoding="utf-8",
    )


class SkillModelValidationTests(unittest.TestCase):
    def test_workflow_and_stack_skills_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)
            _write_skill(root, "workflow-review")
            _write_skill(root, "stack-python")
            proj_path = root / ".agents/project.json"
            proj = json.loads(proj_path.read_text(encoding="utf-8"))
            proj["skills"]["workflow"].append("workflow-review")
            proj["skills"]["stack"].append("stack-python")
            proj_path.write_text(json.dumps(proj, indent=2) + "\n", encoding="utf-8")

            self.assertEqual(validate_mod.validate(root), [])

    def test_virtual_assistant_skill_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)
            _write_skill(root, "virtual-assistant-developer")

            errors = validate_mod.validate(root)
            self.assertTrue(any("virtual-assistant-* skills are no longer supported" in err for err in errors))

    def test_unknown_skill_prefix_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)
            _write_skill(root, "helper-review")

            errors = validate_mod.validate(root)
            self.assertTrue(any("unsupported skill prefix" in err for err in errors))

    def test_old_project_json_skill_groups_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)
            proj_path = root / ".agents/project.json"
            proj = json.loads(proj_path.read_text(encoding="utf-8"))
            proj["skills"]["virtual-assistant"] = ["virtual-assistant-developer"]
            proj_path.write_text(json.dumps(proj, indent=2) + "\n", encoding="utf-8")

            errors = validate_mod.validate(root)
            self.assertTrue(any("unsupported skills group 'virtual-assistant'" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
