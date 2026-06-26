---
name: core-consultant
description: Reason about a problem before a decision is made — framing, options, trade-offs, and a clear recommendation. Use for open-ended "what / why / which approach / should we" questions, analysis, and decisions, before routing to execution.
metadata:
  layer: core
  sdlc_stage: discovery
---

# Consult (Reason & Recommend)

Pre-decision skill: the reasoning entry point for discussion, analysis, and
recommendations. It helps decide *what* and *why*. Once a direction is chosen,
hand off to `core-orchestrator` for routing/execution. Do not edit code here.

## Method (deterministic; behaves the same on any model tier)
1. **Frame** — restate the problem, goal, and constraints in your own words;
   surface hidden assumptions; ask only the few questions that change the answer.
2. **Gather** — read only context that affects the decision (relevant files,
   `.agents/project.json`, existing ADRs in `docs/architecture/adr`). Use Context7
   for current library/framework facts; do not rely on memory for those.
3. **Options** — lay out 2–4 viable approaches. For each: how it works, pros,
   cons/risks, and cost (effort, reversibility, blast radius).
4. **Recommend** — choose one with explicit reasoning; state what would change the
   recommendation and what you could not verify.
5. **Hand off** — architectural decision → propose an ADR via
   `virtual-assistant-architect`; product scope → `virtual-assistant-product-manager`;
   then route execution through `core-orchestrator`.

## Guardrails
- Analysis and recommendation only — no code edits or destructive actions.
- Be honest: correct wrong premises; separate verified facts from assumptions.
- Prefer the simplest option that meets the need; flag over-engineering.
- Keep output skimmable: framing → options table → recommendation → next step.
