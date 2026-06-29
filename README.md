# agentkit-core

A provider-agnostic **agent context kit**. You author your project's agent
context once in a canonical `.agents/` tree + `AGENTS.md`; agentkit generates the
per-provider adapters (Kiro, Claude, Codex, opencode, Antigravity) and keeps them
in sync. It helps you bootstrap durable agent context, optional workflow/stack
skills, memory, docs, MCP, and permissions without locking you to one provider.

## Why

- **One source of truth.** Edit `.agents/**` + `AGENTS.md`; never hand-edit
  generated adapters.
- **Layered & reusable.** A small agnostic **Core**, workflow/stack **Presets**, and a
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
agentkit init --preset preset-angular

# existing project
cd existing-project
agentkit init           # idempotent — never overwrites your files
agentkit presets add preset-spring-boot

# day-to-day: edit AGENTS.md / .agents/** (the source), then
agentkit sync           # regenerate adapters
agentkit validate       # check sync + contracts
agentkit agents generate --provider codex  # generate project-scoped Codex subagents
```

| Command | Does |
|---------|------|
| `agentkit init` | bootstrap a blank project or adapt an existing one |
| `agentkit init --preset <name>` | bootstrap and apply one or more presets |
| `agentkit sync` | regenerate provider adapters (`--check` to verify only) |
| `agentkit validate` | validate canonical context + adapter sync |
| `agentkit upgrade` | refresh kit-managed files to the installed version |
| `agentkit presets list` | show bundled presets |
| `agentkit presets add <name>` | apply a preset to an initialized project |
| `agentkit skills list` | show installed project skills |
| `agentkit manifest new --preset <name>` | write a starter `agentkit.yaml` |
| `agentkit agents generate --provider codex` | generate Codex project custom agents (`--check` to verify only) |

Full guide: [docs/usage.md](docs/usage.md). `init` reads an optional
`agentkit.yaml` manifest for fully non-interactive setup, including **presets** —
declare `preset-spring-boot` or `preset-angular` to add stack skills (plus their
MCP/commands) automatically, or `preset-workflow-standard` to add the standard
explore/plan/implement/review workflow skills.

## Layers

| Layer | What it is | Owned by |
|-------|------------|----------|
| **Core** | bootstrap, sync, validation, memory/docs/MCP/permissions, adapter generation | upstream (this repo) |
| **Workflow skill** (`workflow-*`) | reusable task workflow/instructions | you / community |
| **Stack skill** (`stack-*`) | framework/language/platform conventions | you / community |

## Documentation

By audience (see [docs/](docs/README.md)):

- **Using agentkit** (your projects) → [docs/usage.md](docs/usage.md)
- **Building presets & skills** → [docs/authoring.md](docs/authoring.md)
- **Developing the core** → [docs/development.md](docs/development.md) · [CONTRIBUTING.md](CONTRIBUTING.md)
- **Reference** → [concepts](docs/concepts.md), [upgrade](docs/upgrade.md), [PRD](docs/product/prd.md), [ADRs](docs/architecture/adr/README.md)

## License

MIT.
