# ADR-0003: Codex-only generated custom agents

> Status: accepted
> Date: 2026-06-29
> Supersedes: -
> Superseded-by: -

## Context

ADR-0002 separated project skills from delegated workers. Skills are
provider-agnostic workflow or stack instructions; subagents/custom agents are
provider-specific workers with their own file formats and runtime behavior.

The Codex custom-agent format is verified for project-scoped TOML files under
`.codex/agents/` with `name`, `description`, and `developer_instructions`.
Equivalent Claude/Kiro delegation file formats are not yet verified.

## Decision

Add `agentkit agents generate --provider codex`.

The command writes four generated Codex custom agents:

- `.codex/agents/explorer.toml`
- `.codex/agents/planner.toml`
- `.codex/agents/implementer.toml`
- `.codex/agents/reviewer.toml`

Each file carries an agentkit generated marker and defines `name`, `description`,
and `developer_instructions`. `--check` validates drift without writing.

Existing custom-agent files without an agentkit marker are never overwritten.
`--provider claude` and `--provider kiro` fail clearly as unsupported.

## Consequences

**Positive**: projects get useful Codex delegation roles without confusing them
with reusable workflow skills. Drift is testable, and user-owned agent files are
protected.

**Trade-offs**: custom-agent generation is currently Codex-only. Provider parity
waits on verified provider-specific formats instead of guessing.
