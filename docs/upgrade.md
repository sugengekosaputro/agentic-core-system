# Upgrade

agentkit-core and each preset are versioned with semver. A project records the
resolved versions and a `kitManaged` file list in `.agents/project.json`.

## What `agentkit upgrade` does

- Refreshes **kit-managed** files: the core skills
  (`core-init`/`core-consultant`/`core-orchestrator`), `.agents/README.md`, the git
  hooks, and the **`AGENTS.md` core region** (the text between the `agentkit:core`
  markers). Then it re-runs `sync`.
- Leaves **project-owned** content untouched: the `AGENTS.md` **project region**,
  `permissions.json`, `provider-overrides.json`, `.agents/mcp/servers.json`,
  `docs/`, `.agents/project.json`, and any `virtual-assistant-*` / `stack-*` skills
  (so your customizations and preset edits are safe).

It prints the list of files it refreshed; review the diff, then commit.

## Resolve-then-vendor

`init`/`upgrade` resolve versions and copy the result into the project, so the
project is self-contained at runtime (no live dependency on the kit repo).

## Notes

- Preset-provided skills (`virtual-assistant-*`, `stack-*`) are project-owned and
  are **not** auto-overwritten by `upgrade`, to protect your edits. Re-running
  `agentkit init` re-applies missing preset pieces without clobbering existing files.
