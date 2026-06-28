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
    def test_core_skills_match_templates(self):
        template_core = REPO / "agentkit/templates/skills/core"
        for skill_dir in sorted(template_core.iterdir()):
            if not skill_dir.is_dir():
                continue
            src = skill_dir / "SKILL.md"
            vendored = REPO / ".agents/skills" / skill_dir.name / "SKILL.md"
            self.assertTrue(vendored.exists(), f"{vendored} missing — run `agentkit upgrade`")
            self.assertEqual(
                vendored.read_text(encoding="utf-8"),
                src.read_text(encoding="utf-8"),
                f"{skill_dir.name} drifted from its template — edit the template, then `agentkit upgrade`",
            )

    def test_agents_readme_matches_template(self):
        self.assertEqual(
            (REPO / ".agents/README.md").read_text(encoding="utf-8"),
            (REPO / "agentkit/templates/agents-README.md").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
