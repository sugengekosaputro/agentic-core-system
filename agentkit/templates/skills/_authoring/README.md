# Authoring skills

Skills are progressively-loaded instruction bundles. The agent reads only the
front-matter `name` + `description` at startup; the body loads on demand.

## Rules

1. **Layer prefix** = first segment of the name:
   - `workflow-*` - reusable task workflow or methodology.
   - `stack-*` — technology conventions for a specific framework/language. From a
     stack preset (e.g. `preset-spring-boot`).
2. **`name` must equal the directory name** and be lowercase-hyphen
   (`^[a-z0-9]+(-[a-z0-9]+)*$`). Discovery is one level deep: `skills/<name>/SKILL.md`.
3. **`description` is a trigger sentence** — what it does + WHEN to use it. It is
   always loaded, so keep it specific and short.
4. **Keep `SKILL.md` lean**; put heavy detail in `references/*.md` and load it only
   when that part of the task is in scope.
5. **Write deterministically** (numbered steps, explicit criteria) so the skill
   behaves the same across model tiers and thinking levels.
6. Run `agentkit validate` — it enforces name/format, uniqueness, and sync.

Start from `SKILL.skeleton.md`.
