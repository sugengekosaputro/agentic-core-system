# agentkit-core

A provider-agnostic **agent context kit**. You author your project's agent
context once in a canonical `.agents/` tree + `AGENTS.md`; agentkit generates the
per-provider adapters (Kiro, Claude, Codex, opencode, Antigravity) and keeps them
in sync. It helps you **set up a project, analyze problems, decide tasks, and
develop** — adapting to your stack instead of a fixed one.

## Why

- **One source of truth.** Edit `.agents/**` + `AGENTS.md`; never hand-edit
  generated adapters.
- **Layered & reusable.** A small agnostic **Core**, framework **Presets**, and a
  declarative **Manifest** — see `docs/architecture/`.
- **Safe upgrades.** Versioned core + presets; `upgrade` touches only kit-managed
  files, never your project content.

## Install

```sh
pipx install agentkit-core      # Python CLI
# or, zero-install:
npx agentkit init               # thin Node wrapper over the same engine
```

## Usage

```sh
agentkit init        # bootstrap a blank project or adapt an existing one
agentkit validate    # check canonical context + generated adapters are in sync
agentkit upgrade     # update kit-managed files to newer core/preset versions
agentkit sync        # regenerate adapters from the canonical sources
```

`init` reads a manifest (`agentkit.yaml`) so setup can be fully non-interactive.

## Layers

| Layer | What it is | Owned by |
|-------|------------|----------|
| **Core** (`core-*`) | engine + agnostic skills (init, consultant, orchestrator) | upstream (this repo) |
| **Preset** (`stack-*`) | framework overlays (e.g. spring-boot, angular) | you / community |
| **Virtual assistant** (`virtual-assistant-*`) | reusable job-function methodology (BA, architect, developer, …) | preset-base |

## Documentation

See `docs/` — concepts, the architecture ADR, the authoring guide, and the
upgrade guide.

## License

MIT.
