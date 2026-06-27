---
name: virtual-assistant-developer
description: Implement and refactor features end to end following project conventions. Use for general feature work, bug fixes, refactors, and verification once requirements/design exist. Defer technology rules to the relevant stack-* skill.
metadata:
  layer: virtual-assistant
  sdlc_stage: build
  consumes: docs/architecture/adr
---

# Developer

## Method
1. Confirm requirements (`docs/requirements`) and decisions (`docs/architecture/adr`) are clear.
2. Read the relevant `stack-*` skill for technology conventions; follow them.
3. Make the smallest correct change; match the existing style.
4. Add or adjust tests; run the project's build/verify command.
5. Verify before finishing; clean up temporary artifacts.

## Hand-offs
Use `stack-*` for technology specifics; route via `core-orchestrator` when the
path is unclear.
