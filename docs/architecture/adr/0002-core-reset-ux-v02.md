# ADR-0002: Core reset, workflow/stack skills, and delegation boundary

> Status: accepted
> Date: 2026-06-29
> Supersedes: ADR-0001
> Superseded-by: -

## Context

The v0.1 model proved the canonical `.agents` source and generated provider
adapters, but the default project skills blurred two different ideas:
instructions that guide the current agent, and actual delegated workers. The
`virtual-assistant-*` naming also made presets look like fake personas instead of
reusable workflows.

## Decision

agentkit v0.2 keeps the stable core: `init`, `sync`, `validate`, `upgrade`,
generated adapters, project facts, MCP, permissions, memory, docs, and git hooks.
Core no longer ships default project-local skills.

Project skills use two prefixes only:

- `workflow-*` for reusable task workflows and instructions.
- `stack-*` for technology conventions.

`.agents/project.json` records:

```json
{
  "skills": {
    "workflow": [],
    "stack": []
  }
}
```

Preset application and validation reject old or unknown prefixes, including
`core-*` and `virtual-assistant-*`. `preset-base` is removed without a compatibility
alias.

The CLI adds discovery and incremental UX: `presets list`, `presets add`,
`skills list`, `init --preset`, and `manifest new --preset`.

Delegation is explicitly separate. Skills are workflows/instructions. Subagents or
custom agents are provider-specific workers with separate prompts and tool policy.
The next feature is `agentkit agents generate`, first targeting Codex project-level
custom agents after format verification. Proposed generated workers are
`explorer`, `planner`, `implementer`, and `reviewer`; Claude/Kiro equivalents need
separate provider verification.

## Consequences

**Positive**: default installs are smaller and more truthful; users can inspect and
apply presets without authoring YAML; validation catches stale skill models.

**Negative / trade-offs**: this is a hard break for projects that installed
`virtual-assistant-*`; migration is manual, and `upgrade` must not delete user
files automatically.
