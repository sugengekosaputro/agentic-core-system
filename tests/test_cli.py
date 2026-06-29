"""CLI coverage for preset, skill, init, and manifest UX."""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from agentkit import cli


@contextlib.contextmanager
def _cwd(path: Path):
    old = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def _run_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = cli.main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


class CliUxTests(unittest.TestCase):
    def test_presets_list_shows_bundled_stack_presets(self):
        code, out, err = _run_cli(["presets", "list"])

        self.assertEqual(code, 0, err)
        self.assertIn("preset-angular", out)
        self.assertIn("preset-spring-boot", out)
        self.assertIn("preset-workflow-standard", out)
        self.assertIn("workflow", out)
        self.assertNotIn("preset-base", out)

    def test_presets_add_applies_and_syncs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            with _cwd(root):
                self.assertEqual(_run_cli(["init"])[0], 0)
                code, out, err = _run_cli(["presets", "add", "preset-angular"])

            self.assertEqual(code, 0, err)
            self.assertIn("applied preset preset-angular", out)
            self.assertTrue((root / ".agents/skills/stack-angular/SKILL.md").exists())
            proj = json.loads((root / ".agents/project.json").read_text(encoding="utf-8"))
            self.assertIn("stack-angular", proj["skills"]["stack"])

    def test_skills_list_groups_installed_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            with _cwd(root):
                self.assertEqual(_run_cli(["init", "--preset", "preset-angular"])[0], 0)
                code, out, err = _run_cli(["skills", "list"])

            self.assertEqual(code, 0, err)
            self.assertIn("workflow:\n  (none)", out)
            self.assertIn("stack:\n  stack-angular", out)

    def test_init_preset_prints_next_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            with _cwd(root):
                code, out, err = _run_cli(["init", "--preset", "preset-angular"])

            self.assertEqual(code, 0, err)
            self.assertIn("Canonical context: AGENTS.md and .agents/", out)
            self.assertIn("Installed presets: preset-angular", out)
            self.assertIn("Installed skills: stack-angular", out)
            self.assertIn("Next command: agentkit validate", out)

    def test_manifest_new_preset_writes_expected_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            with _cwd(root):
                code, out, err = _run_cli(["manifest", "new", "--preset", "preset-angular"])

            self.assertEqual(code, 0, err)
            self.assertIn("wrote", out)
            text = (root / "agentkit.yaml").read_text(encoding="utf-8")
            self.assertIn('version: "0.2.0"', text)
            self.assertIn('name: "preset-angular"', text)
            self.assertIn('language: "typescript"', text)
            self.assertIn('framework: "angular"', text)
            self.assertIn('verify: "npm run build"', text)

    def test_agents_generate_codex_and_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            with _cwd(root):
                code, out, err = _run_cli(["agents", "generate", "--provider", "codex"])
                check_code, check_out, check_err = _run_cli(["agents", "generate", "--provider", "codex", "--check"])

            self.assertEqual(code, 0, err)
            self.assertIn("generated codex agents", out)
            self.assertTrue((root / ".codex/agents/explorer.toml").exists())
            self.assertEqual(check_code, 0, check_err)
            self.assertIn("codex agents are in sync", check_out)

    def test_agents_generate_unsupported_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            with _cwd(root):
                code, out, err = _run_cli(["agents", "generate", "--provider", "kiro"])

            self.assertEqual(code, 1)
            self.assertEqual(out, "")
            self.assertIn("unsupported agent provider: kiro", err)


if __name__ == "__main__":
    unittest.main()
