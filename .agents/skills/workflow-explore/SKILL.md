---
name: workflow-explore
description: Read-heavy discovery workflow for mapping a repository, tracing behavior, and identifying constraints before planning or editing.
metadata:
  layer: workflow
  sdlc_stage: discovery
---

# Explore workflow

## Method
1. Restate the concrete question or objective and the boundary of the search.
2. Inspect the smallest useful set of files first: entrypoints, tests, docs, config,
   schemas, and recent related changes.
3. Prefer structural search (`rg`, file listings, symbols, tests) over broad reading.
4. Track facts with file references and separate confirmed behavior from inference.
5. Return findings, unknowns, risks, and the next best action; avoid editing unless
   explicitly asked.

## Output
Summarize what matters for the next step: relevant files, current behavior,
constraints, likely change points, and unresolved questions.
