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
| Core | n/a | bootstrap, sync, validation, memory/docs/MCP/permissions, adapter generation | agentkit-core |
| Workflow | `workflow-*` | reusable task workflow/instructions | a workflow preset or project |
| Stack | `stack-*` | technology conventions (spring-boot, angular, ...) | a stack preset or project |

Core is minimal and agnostic. Workflow and stack skills are **opt-in**, scaffolded
per project from presets or written locally.

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

## Memory

`.agents/memory/journal.md` carries cross-session working continuity (current state
+ an append-only log). It is **read on demand**, not loaded every turn, so it costs
no tokens during normal work, and `validate` keeps it bounded. Decisions still go to
ADRs and facts to `project.json` — the journal is for continuity and pointers only.
`project.json` records the chosen `memory.scope` (workspace / agent / both).

## Skills vs delegation

Skills are workflows and instructions. They guide the current agent when a task
needs a reusable method or stack convention.

Subagents/custom agents are actual workers. They can have separate prompts, tool
policies, and delegation boundaries, but those formats are provider-specific.
agentkit keeps this separate from adapter sync.

`agentkit agents generate --provider codex` writes project-scoped Codex custom
agents under `.codex/agents/`: `explorer`, `planner`, `implementer`, and
`reviewer`. `--check` verifies drift without writing. Existing files without an
agentkit marker are never overwritten.

Claude/Kiro delegation generation is intentionally unsupported until those
provider-specific formats are verified.
