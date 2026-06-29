# PRD: agentkit (lite)

> Status: draft
> Date: 2026-06-27
> Owner: Product Manager

## Problem

Agent context for a project — instructions, skills, MCP servers, permissions — is
fragmented across each AI provider and usually tangled with one codebase. That
makes it hard to reuse, maintain, and update consistently. agentkit-core is the
single, versioned, provider-agnostic kit you drop into any project.

## Users

- **Builder/developer** using the kit on their own project (set up, analyze,
  decide, develop — adapting to their stack).
- **Core maintainer** (kit owner) who evolves core + official presets.
- **Preset author/community** who extends the kit for a stack without touching core.

## Goals

1. One canonical source → generated provider adapters.
2. A small agnostic Core for bootstrap, sync, validation, memory, docs, MCP, and permissions.
3. Opt-in workflow/stack skills, scaffolded per project from presets + a manifest.
4. Safe, versioned upgrades that touch only kit-managed files.
5. Clear, unified docs that double as onboarding.
6. Provider-specific delegation where formats are verified, kept separate from skills.
7. Extensible by design (schemas, templates, tests, validation).

## Non-goals

- Not a multi-framework source-code generator (delegate to official tools +
  Context7).
- Not a runtime dependency on the core repo (resolve-then-vendor).
- Not full skill parity on Antigravity (instructions-only; accepted gap).

## Scope — MVP

- `agentkit-core`: engine, validator, hooks, base governance, base MCP
  (filesystem + context7), CLI (installed via pipx). **Done.**
- `preset-spring-boot` (minimal) and `preset-angular` (frontend prototype). **Done.**
- `preset-workflow-standard` and Codex custom-agent generation. **Done.**

## Success criteria

- `init` on a blank or existing project yields working, in-sync adapters for all
  providers (validator + sync-check green). ✓ verified by the init integration test.
- Core ships no default project-local skills; workflow and stack concerns live in presets.
- `upgrade` updates kit-managed files while leaving project content untouched.

## Open questions

- Memory: **built** — workspace `.agents/memory/journal.md` (on-demand, bounded) + `memory.scope` in the manifest; agent-global scope documented for later.
- npm/npx distribution — deferred; Python/pipx is the only supported path for now
  (npx adds confusion for a Python tool without removing the Python dependency).

See `docs/architecture/adr/0001-agentkit-architecture.md`.
