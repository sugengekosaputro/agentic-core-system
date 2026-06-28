# Agent Context Source

`AGENTS.md` and this `.agents/` tree are the canonical source for all agent CLI
context in this repository. Provider-native files for Codex, Claude, opencode,
Kiro, and Antigravity are **generated adapters**.

Edit only these source files when changing agent behavior: `AGENTS.md`,
`.agents/skills/**`, `.agents/mcp/servers.json`, `.agents/permissions.json`,
`.agents/provider-overrides.json`, `.agents/README.md`. Then run:

```sh
agentkit sync        # regenerate adapters
agentkit validate    # check sync + canonical contracts
```

Provider-specific overrides describe capability gaps only; they must not duplicate
general repository instructions from `AGENTS.md`.

## Skill Taxonomy and Naming

Skills live flat at `.agents/skills/<name>/SKILL.md`. Discovery is one level deep,
so categories are expressed by a name prefix, never by subdirectories:

- `core-*` — how the agent itself works (shipped by agentkit-core, reusable):
  `core-init`, `core-consultant`, `core-orchestrator`.
- `virtual-assistant-*` — job-function methodology (from `preset-base`):
  `virtual-assistant-product-manager`, `-business-analyst`, `-architect`,
  `-developer`, `-qa`, `-security`, `-devops`.
- `stack-*` — project/technology conventions (from a stack preset): e.g.
  `stack-springboot`, `stack-angular`.

Naming rule: `<layer>-<purpose>`, lowercase with single hyphens, matching the skill
directory name. `<purpose>` must be immediately understandable — a real job title,
a real technology name, or a plain verb/noun. Avoid coined jargon and project-name
prefixes. Keep names short.

## Skill Metadata

`SKILL.md` front-matter may carry an optional `metadata` map (recognized by
opencode, ignored safely elsewhere):

    metadata:
      layer: virtual-assistant     # core | virtual-assistant | stack
      sdlc_stage: analysis         # discovery|analysis|design|build|test|secure|deploy|operate
      consumes: docs/product       # artifacts this skill reads
      produces: docs/requirements  # artifacts this skill writes

Output per layer: `core-*` produces decisions/behavior, `virtual-assistant-*`
produces documents under `docs/`, `stack-*` produces code/config.

## Project Artifacts (`docs/`)

Deliverables are NOT skills; they live under `docs/`, organized by owning
virtual-assistant. See `docs/README.md` for the full map.

## ADR Convention

Decisions are ADRs in `docs/architecture/adr/NNNN-short-title.md`. Status lifecycle:
`proposed -> accepted -> superseded by ADR-NNNN | deprecated | rejected`. Only
`accepted` ADRs are in force. Never edit an accepted ADR's decision body; supersede
it with a new ADR and update the index. Keep decision memory in ADRs, change history
in git, conventions in `stack-*` skills — never inline them into `AGENTS.md`.

## Provider Capability Matrix

What each provider consumes (✅ wired · ⚠️ partial · ❌ none):

| Provider | Instructions | MCP | Skills | Permissions |
|----------|--------------|-----|--------|-------------|
| Kiro | ✅ AGENTS.md + steering | ✅ `.kiro/settings/mcp.json` | ✅ `.kiro/skills` symlink | ✅ via `<project>-maintainer` agent `toolsSettings.shell`; default agent prompts for all shell (safe) |
| Claude | ✅ `CLAUDE.md` → AGENTS.md | ✅ `.mcp.json` | ✅ `.claude/skills` symlink | ✅ `.claude/settings.json` |
| Codex | ✅ native AGENTS.md | ✅ `.codex/config.toml` (from example) | ⚠️ `.agents/skills` (verify discovery) | ✅ `.codex/rules/git-approval.rules` |
| opencode | ✅ native AGENTS.md | ✅ `opencode.json` | ✅ native `.agents/skills` | ✅ `opencode.json` `permission.bash` |
| Antigravity | ✅ `context.fileName` | ✅ `.antigravity/settings.json` | ❌ none (AGENTS.md only) | ❌ none |
