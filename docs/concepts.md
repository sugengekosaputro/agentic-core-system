# Concepts

## Canonical → adapter

You author agent context once in a canonical source and generate per-provider
adapters from it:

- **Canonical**: `AGENTS.md` + `.agents/**` (skills, `mcp/servers.json`,
  `permissions.json`, `provider-overrides.json`, `project.json`).
- **Generated adapters** (never hand-edited): `.codex/`, `CLAUDE.md` + `.claude/`,
  `opencode.json`, `.kiro/`, `.antigravity/`, `.mcp.json`.

`agentkit sync` regenerates adapters; `agentkit validate` checks that the canonical
source is well-formed and the adapters are in sync.

## Layers

| Layer | Prefix | What | Source |
|-------|--------|------|--------|
| Core | `core-*` | agent operations: init, consultant, orchestrator | agentkit-core |
| Virtual assistant | `virtual-assistant-*` | job-function methodology (BA, architect, developer, …) | preset-base |
| Stack | `stack-*` | technology conventions (spring-boot, angular, …) | a stack preset |

Core is minimal and agnostic. Roles and stacks are **opt-in**, scaffolded per
project from presets.

## Manifest

`agentkit.yaml` (human-authored) declares the core version, presets, and project
facts. `agentkit init` resolves it into `.agents/project.json` (machine state),
including the `kitManaged` file list that `upgrade` is allowed to overwrite.

## Permissions

`.agents/permissions.json` is the single git-permission policy (inspection → allow,
mutations → ask). The engine maps it to each provider: Claude `settings.json`,
Codex rules, opencode `permission.bash`, and a Kiro custom agent's
`toolsSettings.shell`. The Kiro *default* agent is unaffected and keeps prompting.

## Context budget

`AGENTS.md` loads every turn, so `validate` enforces a size budget (≤ 7000 bytes).
Detail belongs in skill `references/` (loaded on demand) and `docs/`.
