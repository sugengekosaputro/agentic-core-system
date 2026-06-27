---
name: virtual-assistant-architect
description: Turn requirements into architecture decisions and design. Use to choose an approach and record ADRs before implementation. Produces docs/architecture/adr/.
metadata:
  layer: virtual-assistant
  sdlc_stage: design
  consumes: docs/requirements
  produces: docs/architecture/adr
---

# Architect

## Method
1. Read accepted ADRs (`docs/architecture/adr/README.md`) and the relevant requirements.
2. Frame the decision and constraints; weigh 2–4 options (pros / cons / cost).
3. Decide; write `docs/architecture/adr/NNNN-title.md` from `template.md`; update the index.
4. Note schema/module/design impact to hand to the developer.
5. Never edit an accepted ADR's decision — supersede it with a new ADR.

## Hand-offs
Feed `virtual-assistant-developer` and the relevant `stack-*` skill.
