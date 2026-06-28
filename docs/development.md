# Developing agentkit-core

Audience: maintainers/contributors changing **the kit itself** (engine, templates,
core skills, schemas). This is distinct from:

- [Using agentkit](usage.md) — consuming the kit in your own projects.
- [Authoring presets & skills](authoring.md) — building presets/skills on top of core.

## Repo layout

```
agentkit/
  generate_adapters.py   engine: canonical .agents -> provider adapters (parameterized by target root)
  validate.py            canonical contracts + adapter sync checks
  init.py                `init` (scaffold/adapt) and `upgrade` (refresh kit-managed files)
  cli.py                 CLI entrypoint (init|sync|validate|upgrade)
  templates/             everything vendored into a target project on `init`
    AGENTS.base.md, agents-README.md, permissions.json, mcp.base.json,
    provider-overrides.json, env.mcp.example, project.json, agentkit.yaml,
    githooks/, docs/, skills/core/{core-init,core-consultant,core-orchestrator}, skills/_authoring/
  schemas/               JSON Schemas for project.json and the manifest
tests/                   hermetic engine unit tests + init integration tests
docs/                    this documentation
```

The engine never hardcodes a project name: `generate_adapters.project_name()` reads
`.agents/project.json` (falling back to the directory name) and derives the path
placeholder and the Kiro agent name from it.

## This repo dogfoods itself

agentkit-core uses agentkit on itself, so a fresh clone already has `AGENTS.md`,
`.agents/`, and the provider adapters — no `init` needed to start maintaining it.

Important rule: the **source** of what the kit ships is `agentkit/templates/**` and
`agentkit/presets/**`. The repo's own `.agents/**` is **vendored** from those
templates. So:

- Edit the **template** (e.g. `agentkit/templates/skills/core/...`,
  `agentkit/templates/AGENTS.base.md`) — not the vendored copy under `.agents/`.
- Run `agentkit upgrade` to re-sync `.agents/**`, then `agentkit sync` / `validate`.
- `tests/test_dogfood_sync.py` fails if the vendored `.agents` core skills (or
  `.agents/README.md`) drift from the templates, enforcing the rule.

## Dev setup

```sh
git clone <this repo> && cd agentic-core-system
python3 -m venv .venv && . .venv/bin/activate
pip install -e .            # editable: `agentkit` runs from your working tree
python3 -m unittest discover -s tests -v
```

## Make a change, then verify

```sh
# edit agentkit/** or agentkit/templates/**
python3 -m unittest discover -s tests        # unit + integration
# smoke test the consumer flow in a throwaway dir:
mkdir -p /tmp/smoke && cd /tmp/smoke && git init -q
agentkit init && agentkit validate && agentkit sync --check
```

Run `agentkit` only inside a real target project — running it in the kit repo would
scaffold agent context into the kit itself.

## Contracts the tests guard

- `agentkit validate` must stay green: schema, secret-literal, MCP alias/env,
  skill name == directory + lowercase-hyphen, AGENTS.md context budget (≤ 7000 B),
  and adapter sync.
- `agentkit init` must be idempotent and never overwrite existing project files.

## Release

1. Bump the version in `pyproject.toml` and `agentkit/__init__.py`.
2. Update `CHANGELOG.md`.
3. Tag and (when publishing) build/publish to PyPI: `python -m build`. Until
   published, consumers install from a local path or git URL (see
   [usage.md](usage.md#step-3--install-agentkit)).
