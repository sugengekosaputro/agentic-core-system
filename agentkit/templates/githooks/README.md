# Git Hooks (agentkit-core)

Version-controlled git hooks, enabled by `agentkit init` via
`git config core.hooksPath .githooks`. They run at the git layer, so they apply
regardless of which agent/provider or a plain terminal creates the commit/push.

## Hooks

- `pre-commit` — agent-context gate. Runs `agentkit validate` (generator
  `--check` + canonical validation). Blocks the commit if generated adapters or
  skill symlinks drift from the canonical `.agents/**` and `AGENTS.md`. Checks
  only; never rewrites files.
- `pre-push` — source gate. Runs the command at `commands.verify` in
  `.agents/project.json` (set by your preset). Skips if none configured.

## Activation

```sh
git config core.hooksPath .githooks
```

Bypass a single run with `git commit --no-verify` / `SKIP_BUILD_GATE=1 git push`
(not recommended for routine use).
