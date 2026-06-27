# Project status & roadmap

Entry point for resuming work (including in a fresh chat session). Read this first,
then the linked docs. The repository itself is the source of truth — no chat memory
is required to continue.

## Where things stand (v0.1.0)

agentkit-core MVP is implemented and tested locally (not yet pushed/published).

- **Engine**: `agentkit/generate_adapters.py` (canonical → provider adapters,
  parameterized by target root), `agentkit/validate.py` (contracts + sync).
- **CLI**: `agentkit/cli.py` → `init | sync | validate | upgrade`.
- **Bootstrap/upgrade**: `agentkit/init.py` (`run`, `upgrade` incl. AGENTS.md
  core-region merge). **Presets**: `agentkit/presets.py` + `agentkit/presets/`.
- **Templates** shipped to projects: `agentkit/templates/` (AGENTS.base, core
  skills, base MCP = context7+filesystem, docs taxonomy, hooks, schemas).
- **Bundled presets**: `preset-base` (virtual-assistant-*), `preset-spring-boot`
  (minimal), `preset-angular`.
- **Tests**: `tests/` — 15 passing (engine units, init integration incl. non-code
  project, preset apply, upgrade).
- **Docs**: see [docs/README.md](README.md) (usage, authoring, development,
  concepts, upgrade, PRD, [ADR-0001](architecture/adr/0001-agentkit-architecture.md)).

## Locked decisions

- Vocabulary / layers: `core-*` / `virtual-assistant-*` / `stack-*`.
- Distribution: **Python + pipx only** (npm/npx removed; revisit only if decided).
- Resolve-then-vendor: projects are self-contained; no runtime dep on the kit.
- Core stays minimal & general-purpose (code, non-code, research, general use);
  role/stack skills are opt-in via presets.
- Preset metadata is `preset.json`; the user manifest is `agentkit.yaml`.
- Docs organized by audience (using / authoring presets / developing core) and, for
  artifacts, by owning `virtual-assistant-*` then document type.

## Pending / next

1. **Publish** so consumers can install without a local clone: push to GitHub
   (then `pipx install git+URL`), later PyPI (`pipx install agentkit-core`).
2. **`memory` feature** (deferred): workspace `.agents/memory/journal.md` +
   optional agent-global; on-demand (not auto-loaded), size-bounded, pointer-based.
   Decide write discipline before building.
3. **Preset version upgrade**: `upgrade` currently refreshes core-managed files
   only; add opt-in refresh of preset-provided skills/overlays to newer versions.
4. **More presets** as needed (e.g. node, go, python), each via the preset format
   in [authoring.md](authoring.md).

## How to resume in a new chat

1. Open the chat in this repo (`agentic-core-system`).
2. Read this file, then `README.md` and `docs/` (especially ADR-0001 + usage).
3. Run `python3 -m unittest discover -s tests` to confirm a green baseline.
4. Continue from **Pending / next** above.

> History of how we got here lives in `docs/architecture/adr/`, `docs/product/prd.md`,
> and `CHANGELOG.md`. The original extraction runbook is in the springboot-starter
> repo at `docs/operations/agentkit-extraction.md`.
