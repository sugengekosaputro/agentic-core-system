---
name: workflow-plan
description: Planning workflow for turning a clear objective into scoped implementation steps, risks, and verification.
metadata:
  layer: workflow
  sdlc_stage: plan
---

# Plan workflow

## Method
1. Start from confirmed repository facts, not assumptions.
2. Define the intended outcome, non-goals, affected modules, and user-visible behavior.
3. Break the work into ordered steps with a verification point for each risky change.
4. Prefer existing architecture and local helper APIs over new abstractions.
5. Call out tradeoffs, migration concerns, and any decision that needs owner input.

## Output
Produce a short executable plan: steps, touched areas, risks, and verification
commands. Keep the plan current as implementation changes what is known.
