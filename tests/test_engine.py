"""Hermetic unit tests for the adapter engine. Run: python3 -m unittest discover -s tests"""

from __future__ import annotations

import unittest

from agentkit import generate_adapters as gen


class OpencodePermissionTests(unittest.TestCase):
    def test_decision_mapping(self):
        perms = {"rules": {
            "allow": [["git", "status"]],
            "prompt": [["git", "commit"]],
            "deny": [["git", "push", "--force"]],
        }}
        bash = gen.opencode_permission(perms)["bash"]
        self.assertEqual(bash["git status*"], "allow")
        self.assertEqual(bash["git commit*"], "ask")
        self.assertEqual(bash["git push --force*"], "deny")


class OpencodeMcpTests(unittest.TestCase):
    def test_http_to_remote(self):
        s = {"name": "c7", "transport": "http", "url": "https://x/mcp"}
        self.assertEqual(
            gen.mcp_server_for_opencode(s, "/ph"),
            {"type": "remote", "url": "https://x/mcp", "enabled": True},
        )

    def test_stdio_repo_root_substitution(self):
        s = {"name": "fs", "transport": "stdio", "command": "npx", "args": ["-y", "p", "${REPO_ROOT}"]}
        out = gen.mcp_server_for_opencode(s, "/ph")
        self.assertEqual(out["command"], ["npx", "-y", "p", "."])
        self.assertEqual(out["type"], "local")


class ClaudeKiroTests(unittest.TestCase):
    def test_claude_allow_ask(self):
        perms = {"rules": {"allow": [["git", "status"]], "prompt": [["git", "commit"]], "deny": []}}
        out = gen.claude_settings(perms)["permissions"]
        self.assertIn("Bash(git status:*)", out["allow"])
        self.assertIn("Bash(git commit:*)", out["ask"])

    def test_kiro_agent_named_and_mapped(self):
        perms = {"rules": {"allow": [["git", "status"]], "prompt": [["git", "commit"]], "deny": []}}
        agent = gen.kiro_agent(perms, "demo")
        self.assertEqual(agent["name"], "demo-maintainer")
        self.assertIn(r"^git status\b", agent["toolsSettings"]["shell"]["allowedCommands"])
        self.assertNotIn(r"^git commit\b", agent["toolsSettings"]["shell"]["allowedCommands"])
        self.assertNotIn("__generated", agent)


class CodexTests(unittest.TestCase):
    def test_codex_uses_absolute_placeholder(self):
        s = {"name": "fs", "transport": "stdio", "command": "npx", "args": ["-y", "p", "${REPO_ROOT}"]}
        self.assertEqual(gen.command_args(s, "codex", "/path/to/x"), ["-y", "p", "/path/to/x"])


class EnabledServersTests(unittest.TestCase):
    def test_filter(self):
        mcp = {"servers": [{"name": "a", "enabledByDefault": True}, {"name": "b", "enabledByDefault": False}]}
        self.assertEqual([s["name"] for s in gen.enabled_servers(mcp)], ["a"])


if __name__ == "__main__":
    unittest.main()
