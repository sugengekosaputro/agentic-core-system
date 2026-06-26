---
name: core-init
description: Bootstrap or adapt agent context for a project. Use at the very start in a blank project (scaffold) or an existing project (detect stack, map needed skills, audit/consolidate existing agent-context surfaces).
metadata:
  layer: core
  sdlc_stage: discovery
---

# Init / Onboard a Project

One entry point for new and existing projects. Run `agentkit init` for the
mechanical setup (copy base templates, scaffold from the manifest, generate
adapters, enable hooks); use this playbook for the decisions.

## 1. Detect state
Blank (no build files / no `src`) vs existing (has a stack).

## 2. Detect stack (language/framework agnostic)
`pom.xml`→Java/Maven, `build.gradle`→JVM/Gradle, `package.json`→Node,
`go.mod`→Go, `pyproject.toml`/`requirements.txt`→Python, `Cargo.toml`→Rust.
Record findings in `.agents/project.json`.

## 3. Choose presets & skills
- Core ships only `core-*`. Select a **preset** for the detected stack
  (e.g. `preset-spring-boot`, `preset-angular`); `preset-base` provides the
  reusable `virtual-assistant-*` methodology.
- Enable the `virtual-assistant-*` the project needs (`virtual-assistant-developer`
  always; add business-analyst/architect/qa/security/devops as the work demands).
- Add the preset's `stack-*` skills. Follow the naming rule in `.agents/README.md`.

## 4. Blank project
Scaffold via `agentkit init` with a manifest, write `.agents/project.json`,
create the chosen `stack-*` skeletons, generate adapters, set `core.hooksPath`.

## 5. Existing project (adapt)
- Audit existing surfaces (`AGENTS.md`, `CLAUDE.md`, `.cursor`,
  `.github/copilot-instructions.md`, scattered MCP config, ...).
- Classify each fragment: `core` / `virtual-assistant` / `stack` /
  project-knowledge / cruft.
- Reconcile conflicts; flag load-bearing vs stale for human decision — do NOT
  delete unilaterally.
- Fold real content into canonical `.agents/**` + `AGENTS.md`; replace provider
  files with generated adapters. Verify per provider.

## Output
- `.agents/project.json` (project facts, enabled skills, resolved kit versions).
- For existing projects: a consolidation proposal. Deletions require human approval.
