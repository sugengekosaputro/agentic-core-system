---
name: workflow-review
description: Code-review workflow for finding correctness, security, regression, and test coverage issues.
metadata:
  layer: workflow
  sdlc_stage: review
---

# Review workflow

## Method
1. Review the diff and the surrounding code that gives it meaning.
2. Prioritize bugs, behavior regressions, security/privacy issues, data loss, and
   missing tests over style comments.
3. Ground every finding in a concrete file reference and explain the failure mode.
4. Check public interfaces, compatibility, validation paths, and generated artifacts.
5. If no issues are found, say that clearly and identify any remaining test gaps.

## Output
Lead with findings ordered by severity, then open questions or assumptions, then a
brief summary only if it adds useful context.
