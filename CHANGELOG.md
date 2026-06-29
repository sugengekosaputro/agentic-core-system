# Changelog

All notable changes to agentkit-core are documented here. This project follows
[Semantic Versioning](https://semver.org/) and
[Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- Initial extraction of the agent-context engine from the springboot-starter
  prototype: canonical `.agents` → generated provider adapters.
- Layered Core / Preset / Manifest architecture (see `docs/`).
- CLI: `agentkit init | validate | upgrade | sync` (Python, installed via pipx).
- CLI UX v0.2: `agentkit presets list`, `agentkit presets add <name>`,
  `agentkit skills list`, `agentkit init --preset <name>`, and
  `agentkit manifest new --preset <name>`.
- CLI: `agentkit agents generate --provider codex` generates project-scoped Codex
  custom agents (`explorer`, `planner`, `implementer`, `reviewer`), with
  `--check` drift validation and safe handling for unmarked existing files.
- Preset system: additive, idempotent overlays merged into the canonical context
  (skills, MCP servers, env vars, commands, AGENTS.md project region). Bundled
  presets: `preset-workflow-standard`, `preset-spring-boot` (minimal), and
  `preset-angular`.
- Memory: on-demand `.agents/memory/journal.md` (current state + log), size-bounded
  by `validate`; `memory.scope` recorded in `project.json`.
- `agentkit upgrade` merges the AGENTS.md core region and supports
  `--refresh-presets` to update preset-provided skills.
- The repo dogfoods itself: committed `AGENTS.md` + `.agents/` + provider adapters
  (vendored from templates; kept in sync by `agentkit upgrade` and a dogfood test).

### Changed
- Breaking reset to the `0.2.0` project skill model: `.agents/project.json` now
  records `skills.workflow` and `skills.stack`.
- Core no longer ships default project-local skills; durable routing guidance lives
  in `AGENTS.md`, `.agents/README.md`, and docs.

### Removed
- Removed `preset-base` and bundled `virtual-assistant-*` skills. Existing projects
  must migrate those manually to `workflow-*` or `stack-*`.
