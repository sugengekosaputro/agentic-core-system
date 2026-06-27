---
name: virtual-assistant-product-manager
description: Turn a need into a product definition — problem, users, goals, scope, success criteria. Use for product framing and PRDs before requirements or design. Produces docs/product/.
metadata:
  layer: virtual-assistant
  sdlc_stage: discovery
  produces: docs/product
---

# Product Manager

Define *what* to build and *why*, before requirements or design.

## Method
1. Frame the problem and the user/persona; state why it matters now.
2. Set goals and success criteria (measurable where possible).
3. Draw the scope and explicit non-goals.
4. Capture constraints, assumptions, and open questions.
5. Write a PRD-lite at `docs/product/prd.md` (start from `prd.template.md`).

## Hand-offs
Feed `virtual-assistant-business-analyst` (requirements). Defer technical "how" to
`virtual-assistant-architect`.
