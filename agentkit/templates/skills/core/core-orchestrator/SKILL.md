---
name: core-orchestrator
description: Route a request to the right skill and drive multi-step execution, once intent is clear. Use for broad, ambiguous, multi-step, feature, debugging, migration, auth, or skill-selection tasks before planning or editing when the user did not name a specific skill.
metadata:
  layer: core
  sdlc_stage: delivery
---

# Orchestrate Work (Route + Plan)

Post-decision skill: once the goal is known, map intent → skills/tools/plan and
drive execution. For open-ended "what / why / should we" questions that precede a
decision, use `core-consultant` instead.

## Intake (deterministic steps)
1. Restate the concrete outcome in one sentence before opening files.
2. Classify the work: feature/module · data/schema · auth/security · docs/agent ·
   API/integration · pure inspection.
3. Discover available skills from `.agents/project.json` (the `skills` map) and
   each `.agents/skills/*/SKILL.md` description; select only those that match.
4. Inspect local files before planning (prefer ripgrep + targeted reads).
5. Choose execution mode:
   - **Plan first** for ambiguous, broad, security-sensitive, schema-changing, or
     cross-module work.
   - **Execute directly** for small, clear, low-risk edits after selecting skills.
6. If a chosen MCP/tool is unavailable, fall back to local inspection, local
   commands, focused tests, or state the blocker.

## Planning rules
- Keep the plan bound to repo boundaries and the selected skills.
- Name the selected skills/tools when the choice affects the work.
- Read downstream skill references only when that part of the task is in scope.
- Use Context7 for library/framework/SDK/API/CLI/cloud docs before relying on memory.

## Hand-offs
- Need a decision/recommendation first → `core-consultant`.
- Need onboarding/bootstrap → `core-init`.
- Job-function methodology (requirements, design, implementation) →
  `virtual-assistant-*`. Stack-specific conventions → `stack-*`.
