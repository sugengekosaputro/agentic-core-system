# Upgrade

agentkit-core and each preset are versioned with semver. A project records the
resolved versions and a `kitManaged` file list in `.agents/project.json`.

## What `agentkit upgrade` does

- Refreshes **kit-managed** files only: the core skills
  (`core-init`/`core-consultant`/`core-orchestrator`), `.agents/README.md`, and the
  git hooks; then re-runs `sync`.
- Leaves **project-owned** files untouched: `permissions.json`,
  `provider-overrides.json`, `.agents/mcp/servers.json`, `AGENTS.md` (project
  region), `docs/`, and `.agents/project.json`.

## Resolve-then-vendor

`init`/`upgrade` resolve versions and copy the result into the project, so the
project is self-contained at runtime (no live dependency on the kit repo). Commit
the result; review the diff that `upgrade` prints.

## Known limitation (v0.1.0)

The `AGENTS.md` core region (between the `agentkit:core` markers) is not yet
auto-merged on upgrade; update it manually if the core governance text changes.
Tracked as a follow-up.
