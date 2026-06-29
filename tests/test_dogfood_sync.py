"""Dogfood sync: this repo's vendored .agents must match the shipped templates.

The kit dogfoods itself: `.agents/**` is vendored from `agentkit/templates/**`. Edit
the template (the source), then `agentkit upgrade` to re-sync. These tests fail if
the vendored copies drift, so the edit-the-template rule is enforced.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class DogfoodSyncTests(unittest.TestCase):
    def test_default_template_project_skills_are_empty(self):
        self.assertEqual(list((REPO / "agentkit/templates/skills").glob("core/*/SKILL.md")), [])

    def test_dogfood_workflow_skills_match_standard_preset(self):
        expected = [
            "workflow-explore",
            "workflow-implement",
            "workflow-plan",
            "workflow-review",
        ]
        self.assertEqual(
            sorted(p.parent.name for p in (REPO / ".agents/skills").glob("*/SKILL.md")),
            expected,
        )
        for name in expected:
            self.assertEqual(
                (REPO / f".agents/skills/{name}/SKILL.md").read_text(encoding="utf-8"),
                (
                    REPO
                    / f"agentkit/presets/preset-workflow-standard/skills/{name}/SKILL.md"
                ).read_text(encoding="utf-8"),
            )

    def test_agents_readme_matches_template(self):
        self.assertEqual(
            (REPO / ".agents/README.md").read_text(encoding="utf-8"),
            (REPO / "agentkit/templates/agents-README.md").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
