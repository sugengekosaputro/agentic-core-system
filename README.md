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

## Install (once)

agentkit is a Python CLI, installed with [pipx](https://pipx.pypa.io):

```sh
pipx install git+https://github.com/sugengekosaputro/agentic-core-system.git
# from a local clone instead:   pipx install ./agentic-core-system
# after a PyPI release:         pipx install agentkit-core
agentkit --version
```

New to Python or pipx? Follow the step-by-step **[beginner's guide](docs/usage.md)**
— it covers installing Python, pipx, and agentkit from scratch.

## Quickstart

You don't copy this repo into your project. Install the tool once, then run it
**inside** your project — only the generated `.agents/` tree + adapters land there.

```sh
# blank project
mkdir my-app && cd my-app && git init
agentkit init           # scaffold .agents + adapters + hooks
                        # then create code with the official tool (Spring Initializr, ng new, …)

# existing project
cd existing-project
agentkit init           # idempotent — never overwrites your files

# day-to-day: edit AGENTS.md / .agents/** (the source), then
agentkit sync           # regenerate adapters
agentkit validate       # check sync + contracts
```

| Command | Does |
|---------|------|
| `agentkit init` | bootstrap a blank project or adapt an existing one |
| `agentkit sync` | regenerate provider adapters (`--check` to verify only) |
| `agentkit validate` | validate canonical context + adapter sync |
| `agentkit upgrade` | refresh kit-managed files to the installed version |

Full guide: [docs/usage.md](docs/usage.md). `init` reads an optional
`agentkit.yaml` manifest for fully non-interactive setup.

## Layers

| Layer | What it is | Owned by |
|-------|------------|----------|
| **Core** (`core-*`) | engine + agnostic skills (init, consultant, orchestrator) | upstream (this repo) |
| **Preset** (`stack-*`) | framework overlays (e.g. spring-boot, angular) | you / community |
| **Virtual assistant** (`virtual-assistant-*`) | reusable job-function methodology (BA, architect, developer, …) | preset-base |

## Documentation

By audience (see [docs/](docs/README.md)):

- **Using agentkit** (your projects) → [docs/usage.md](docs/usage.md)
- **Building presets & skills** → [docs/authoring.md](docs/authoring.md)
- **Developing the core** → [docs/development.md](docs/development.md) · [CONTRIBUTING.md](CONTRIBUTING.md)
- **Reference** → [concepts](docs/concepts.md), [upgrade](docs/upgrade.md), [PRD](docs/product/prd.md), [ADR-0001](docs/architecture/adr/0001-agentkit-architecture.md)

## License

MIT.
