# Authoring presets & skills

Audience: developers extending the kit with new **skills** or **presets** (on top of
core). For using the kit see [usage.md](usage.md); for changing the core engine
itself see [development.md](development.md).

## A new skill

1. Copy `agentkit/templates/skills/_authoring/SKILL.skeleton.md` to
   `.agents/skills/<name>/SKILL.md`.
2. Pick the layer prefix: `core-*` (kit-owned — don't fork), `virtual-assistant-*`
   (job function), or `stack-*` (technology).
3. `name` must equal the directory name and be lowercase-hyphen. The `description`
   is a trigger sentence (what + WHEN); it loads at startup, so keep it specific.
4. Keep `SKILL.md` lean; put heavy detail in `references/*.md`.
5. Write deterministic, numbered steps so the skill behaves the same on any model tier.
6. Run `agentkit validate`.

## A new preset

A preset is an overlay that adds skills, an MCP overlay, commands, and a profile on
top of core. It must not modify core-managed files (the engine, the three core
skills, the governance region of `AGENTS.md`). Applying a preset is **additive and
idempotent**: skills are copied, MCP servers merged by name, env vars appended,
commands merged, and a note inserted into the AGENTS.md project region — after which
`agentkit sync` keeps every adapter consistent.

Bundled presets live under `agentkit/presets/<name>/`. Layout:

```
preset-<stack>/
  preset.json          name, version, coreVersion, kind (base|stack), language, framework
  skills/<name>/SKILL.md   skills to add (virtual-assistant-* or stack-*), one level deep
  mcp.overlay.json     optional: servers this stack needs (merged by name)
  env.mcp.additions    optional: env var names to document in .env.mcp.example
  commands.json        optional: e.g. { "verify": "..." } -> project.json commands
  agents.project.md    optional: text inserted into the AGENTS.md project region
  profile.json         optional: official initializer + Context7 libs + conventions
```

Metadata is JSON (the engine is standard-library only); the user-facing manifest
(`agentkit.yaml`) is the only YAML. Best practices stay current by fetching official
docs via Context7 at scaffold time rather than freezing framework code in templates.
See `agentkit/presets/preset-spring-boot/` for a complete example.
