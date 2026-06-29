---
name: workflow-implement
description: Implementation workflow for making scoped changes, preserving user work, and verifying locally.
metadata:
  layer: workflow
  sdlc_stage: build
---

# Implement workflow

## Method
1. Re-read the files you will edit and nearby tests before changing code.
2. Keep edits narrow and aligned with existing patterns; avoid unrelated refactors.
3. Preserve user changes and generated files unless the task explicitly owns them.
4. Add or update focused tests when behavior, contracts, or public interfaces change.
5. Run the smallest useful verification first, then broader checks when the blast
   radius warrants it.

## Output
Report changed files, behavior changes, verification commands, and any residual
risk or follow-up that remains.
