"""Integration test: `agentkit init` produces a valid, in-sync context."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agentkit import generate_adapters, init as init_mod, validate as validate_mod


class InitIntegrationTests(unittest.TestCase):
    def test_init_produces_valid_in_sync_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)

            # default init no longer installs project-local skills
            self.assertTrue((root / ".agents/skills").exists())
            self.assertEqual(list((root / ".agents/skills").glob("*/SKILL.md")), [])

            # base files present
            self.assertTrue((root / "AGENTS.md").exists())
            self.assertTrue((root / ".agents/mcp/servers.json").exists())
            self.assertTrue((root / "docs/architecture/adr/template.md").exists())
            self.assertTrue((root / ".agents/memory/journal.md").exists())

            # kiro agent named from the project
            self.assertTrue((root / ".kiro/agents" / f"{root.name}-maintainer.json").exists())

            # adapters in sync and context valid
            self.assertEqual(generate_adapters.sync(root, check=True), [])
            self.assertEqual(validate_mod.validate(root), [])

    def test_init_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root)
            init_mod.run(root)  # second run must not error or change sync state
            self.assertEqual(generate_adapters.sync(root, check=True), [])

    def test_init_works_for_a_non_code_project(self):
        # general / research use: a folder with only notes, no build files
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "notes.md").write_text("# Research notes\n", encoding="utf-8")
            init_mod.run(root)
            self.assertEqual(validate_mod.validate(root), [])
            proj = json.loads((root / ".agents/project.json").read_text())
            self.assertEqual(proj["language"], "")
            self.assertEqual(proj["framework"], "")
            self.assertEqual(proj["skills"], {"workflow": [], "stack": []})

    def test_init_with_preset_applies_stack_preset_without_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root, preset_names=["preset-angular"])

            self.assertTrue((root / ".agents/skills/stack-angular/SKILL.md").exists())
            proj = json.loads((root / ".agents/project.json").read_text())
            self.assertIn("stack-angular", proj["skills"]["stack"])
            self.assertIn({"name": "preset-angular", "version": "0.2.0"}, proj["kit"]["presets"])
            self.assertEqual(validate_mod.validate(root), [])

    def test_init_with_workflow_preset_records_workflows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            init_mod.run(root, preset_names=["preset-workflow-standard"])

            self.assertTrue((root / ".agents/skills/workflow-explore/SKILL.md").exists())
            proj = json.loads((root / ".agents/project.json").read_text())
            self.assertIn("workflow-explore", proj["skills"]["workflow"])
            self.assertIn({"name": "preset-workflow-standard", "version": "0.2.0"}, proj["kit"]["presets"])
            self.assertEqual(validate_mod.validate(root), [])


if __name__ == "__main__":
    unittest.main()
