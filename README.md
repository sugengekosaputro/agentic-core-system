# Agent Instruction Boilerplate

Minimal repository template for sharing one instruction source across agent
providers.

## Files

- `instructions.md` is the source of truth for repository guidance, including a
  portable spec-style workflow for larger features, risky bugs, and ambiguous
  multi-file work.
- `AGENTS.md` points generic agents and Codex-compatible tools to the shared
  instructions.
- `CLAUDE.md` imports the shared instructions for Claude Code.
- `opencode.json` registers the shared instructions for opencode.
- `.codex/config.toml` lets Codex discover `instructions.md` as a project
  instruction fallback.
- `scripts/check_adapters.sh` statically verifies that adapter files stay short,
  pointer-only, and delegated to `instructions.md`.
- `scripts/probe.sh` and `scripts/probe_write.sh` are an optional test lab that
  checks whether providers actually follow `instructions.md`. They do not affect
  agent behavior.

## Provider Matrix

| Provider | Project config | Notes |
| --- | --- | --- |
| Codex | `AGENTS.md`, `.codex/config.toml` | `AGENTS.md` delegates to `instructions.md`; Codex also gets `project_doc_fallback_filenames = ["instructions.md"]`. |
| Claude Code | `CLAUDE.md` | Imports `@instructions.md`. There is no `.claude/` directory because this template does not need project settings or rules. |
| opencode | `opencode.json` | Registers `instructions.md` with the project config schema. There is no `.opencode/` directory because that path is only needed for plugins. |

## Static adapter check

Run this lightweight check after changing adapter or instruction files. It
verifies that adapters stay pointer-only and that `instructions.md` avoids
provider-specific adapter details. It does not call any provider CLI or require
authentication.

```sh
scripts/check_adapters.sh
```

## Behavior probes (optional test lab)

`scripts/` holds a self-contained harness that verifies whether each installed
provider actually honors the `Reasoning & Interaction Contract` and safety rules
in `instructions.md`. These scripts only observe behavior — they are not read by
any provider and have no effect on how agents act.

- `scripts/probe.sh` — read-only probes: challenge / anti-sycophancy / language,
  plan-vs-act, investigate-before-answering, multi-option decision support, and
  prompt-injection resistance.
- `scripts/probe_write.sh` — write probes (needs write permission): verification
  after a code change, matching existing style, no over-engineering, and flagging
  a missing-auth network endpoint. It edits throwaway fixtures under `.probe_tmp/`
  (gitignored) and guards against edits outside that directory.

```sh
# Run against all installed providers
scripts/probe.sh

# Skip or select providers (opencode is skipped by default in probe_write.sh)
SKIP_PROVIDERS="opencode" scripts/probe.sh
PROVIDERS="codex claude" scripts/probe_write.sh
```

Grading is heuristic; the scripts print full provider output so a human can
confirm each verdict. Requires the relevant provider CLIs (`codex`, `claude`,
`opencode`) to be installed and authenticated.

## Use

1. Edit `instructions.md` when repository guidance changes.
2. Keep adapter files short and pointer-only unless a provider changes its
   required syntax.
3. Keep private values in ignored local environment files.

## Updating Provider Adapters

- Keep `instructions.md` provider-neutral — it must not reference specific
  adapter files, provider names, or provider-specific syntax.
- Adapter files should stay short and delegate to `instructions.md`.
- When guidance changes, update `instructions.md` first, then adjust adapters
  only if their pointer syntax changes.
- Do not duplicate full guidance across adapters.
- Run `scripts/check_adapters.sh` after any change to verify integrity.
