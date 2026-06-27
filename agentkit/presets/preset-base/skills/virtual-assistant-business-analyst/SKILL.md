---
name: virtual-assistant-business-analyst
description: Break a product need into user stories and acceptance criteria. Use for requirement analysis and backlog grooming before design or implementation. Produces docs/requirements/.
metadata:
  layer: virtual-assistant
  sdlc_stage: analysis
  consumes: docs/product
  produces: docs/requirements
---

# Business Analyst

## Method
1. Read `docs/product` (the PRD) and restate the goal.
2. Split it into independent user stories ("As a … I want … so that …").
3. Give each story explicit, testable acceptance criteria.
4. Prioritize; note dependencies and edge cases.
5. Write `docs/requirements/NNN-<feature>.md`.

## Hand-offs
Feed `virtual-assistant-architect` (design) and, later, QA (verification).
