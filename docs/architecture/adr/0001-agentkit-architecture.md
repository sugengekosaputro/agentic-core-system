# ADR-0001: agentkit layered architecture (Core / Preset / Manifest)

> Status: accepted
> Date: 2026-06-27
> Supersedes: -
> Superseded-by: -

## Context

agentkit extracts a proven model — canonical `AGENTS.md` + `.agents/**` generating
per-provider adapters — into a standalone, publishable, versioned kit reusable
across projects and extensible by others, while core stays owned upstream.

Constraints: skill discovery is one level deep (`skills/<name>/SKILL.md`); providers
differ (opencode/Kiro/Claude/Codex support skills + permission mapping, Antigravity
is instructions-only); the engine must be parameterized (no hardcoded project name
or agent name) and the pre-push gate must be configurable per project.

## Decision

A shallow, layered architecture with a constrained override surface and
resolve-then-vendor distribution.

- **Core** (`agentkit-core`): engine, validator, hooks, base governance region of
  `AGENTS.md`, base MCP (filesystem + context7), schemas, and three agnostic core
  skills (`core-init`, `core-consultant`, `core-orchestrator`). Semver, owned upstream.
- **Preset** (`preset-<stack>`): a stack overlay declaring a `coreVersion`, adding
  `stack-*` skills, an MCP overlay, commands, and a profile. Forkable without
  touching core.
- **preset-base**: generic overlay holding the reusable `virtual-assistant-*`
  methodology.
- **Manifest** (`agentkit.yaml`): declarative intent consumed by `init`, resolved
  into `.agents/project.json` (state + `kitManaged` file list).

Override is constrained: presets/projects may ADD skills, MCP servers, commands,
and the project region of `AGENTS.md`; they may NOT modify core-managed files
(engine, core skills, governance region). Layers stay shallow: core → preset →
project. Distribution is resolve-then-vendor: projects are self-contained at runtime.

Project code generation is out of scope — delegate to official initializers
(Spring Initializr, Angular CLI) and keep best practices current via Context7;
presets carry declarative profiles, not framework code.

## Consequences

**Positive**: reusable across projects; others extend via presets without touching
core; self-contained, reproducible projects; versioned low-risk upgrades; unified
docs double as onboarding.

**Negative / trade-offs**: more moving parts than a single template repo; requires a
precise kit-managed vs project-owned manifest and merge rules; marked regions in
`AGENTS.md` add a small authoring constraint.

**Status of follow-ups**: engine parameterization, base MCP trim, configurable
pre-push, the three core skills, CLI (init/validate/sync/upgrade), the init
integration test, the preset engine, and the bundled presets (`preset-base`,
`preset-spring-boot`, `preset-angular`) are **done**. Pending: `AGENTS.md`
core-region auto-merge on upgrade, and the reserved `memory` feature. Deferred:
npm/npx distribution (Python/pipx only for now).
