# Usage (for consumers)

How to use agentkit-core in your own projects. You do **not** copy this repo into
your project. agentkit is installed once as a tool; you run it inside your project,
and only its output (a vendored `.agents/` tree + generated adapters) lands there.

## Mental model

| Thing | Where it lives | Role |
|-------|----------------|------|
| `agentkit-core` repo | upstream (maintained by the kit owner) | source of truth; consumers don't touch it |
| `agentkit` tool | your machine (pipx / npx) | the engine + templates |
| Your project | your working directory | receives `.agents/` + adapters via `agentkit init` |

The result is **self-contained**: at runtime your AI provider reads the vendored
files; there is no live dependency on the kit repo.

## 1. Install the tool (once)

```sh
pipx install agentkit-core        # recommended
# or zero-install:
npx agentkit <command>            # thin Node wrapper over the same Python engine
```

> Not yet published to PyPI/npm. Until then, install from source:
> `pipx install /path/to/agentic-core-system` (or a git URL). After publish:
> `pipx install agentkit-core`.

## 2a. Blank project

```sh
mkdir my-app && cd my-app && git init
# optional: an agentkit.yaml manifest for non-interactive setup (see below)
agentkit init
# then create the actual code with the ecosystem's official tool, e.g.
#   Spring Boot -> Spring Initializr     Angular -> ng new
```

`init` scaffolds `.agents/**`, generates every provider adapter, seeds
`.agents/project.json`, and enables the git hooks. The project directory must
exist first (you create it); the core repo is never copied in.

## 2b. Existing project

```sh
cd existing-project
agentkit init        # idempotent — never overwrites files you already have
agentkit validate
```

To consolidate scattered legacy agent context (CLAUDE.md, `.cursor`,
`.github/copilot-instructions.md`, ad-hoc MCP config), let the agent follow the
`core-init` skill: audit → classify → fold into canonical `.agents/**`. Deletions
require your approval.

## 3. Day-to-day loop

```sh
# edit the SOURCE only: AGENTS.md and .agents/** (never edit generated adapters)
agentkit sync         # regenerate all provider adapters
agentkit validate     # check sync + canonical contracts
git add -A && git commit   # the pre-commit hook blocks drift
```

## 4. Manifest (optional, for automatic setup)

Create `agentkit.yaml` before `init` to drive non-interactive setup:

```yaml
core:
  version: "0.1.0"
presets:
  - { name: preset-base, version: "0.1.0" }
project:
  name: my-app
  language: ""          # e.g. java, typescript
  framework: ""         # e.g. spring-boot, angular
  commands:
    verify: ""          # pre-push gate, e.g. "./mvnw -q test -Dtest=ArchitectureTest"
memory:
  scope: both
```

`init` resolves this into `.agents/project.json` (machine state). Without a
manifest, `init` seeds sensible defaults from the directory name.

## 5. Updating the kit later

```sh
pipx upgrade agentkit-core    # get a newer tool version
cd my-app && agentkit upgrade # refresh ONLY kit-managed files; your content is untouched
```

Kit-managed files (recorded in `.agents/project.json` `kitManaged`) are the core
skills, `.agents/README.md`, and the git hooks. Your `permissions.json`,
`AGENTS.md` project region, `docs/`, and stack skills are left alone. Review the
diff `upgrade` prints, then commit.

## 6. Presets (coming)

Presets add stack conventions on top of core. Once available, declare them in
`agentkit.yaml`:

```yaml
presets:
  - { name: preset-spring-boot, version: "0.1.0" }
```

`init` then vendors the preset's `stack-*` skills, MCP overlay (e.g. postgres),
and build/verify commands (resolve-then-vendor). With no preset, `init` gives you
the agnostic core only (`core-init`, `core-consultant`, `core-orchestrator`).

## Commands reference

| Command | Does |
|---------|------|
| `agentkit init` | bootstrap a blank project or adapt an existing one |
| `agentkit sync` | regenerate provider adapters from `.agents` (`--check` to verify only) |
| `agentkit validate` | validate canonical context + adapter sync |
| `agentkit upgrade` | refresh kit-managed files to the installed version |

## Troubleshooting

- **"agentkit: command not found"** — ensure `pipx`'s bin dir is on `PATH`
  (`pipx ensurepath`), or use `npx agentkit ...`.
- **npx run** needs Python 3.10+; the wrapper installs the Python package on first
  use.
- **pre-commit blocks the commit** — run `agentkit sync`, re-stage, commit again.
