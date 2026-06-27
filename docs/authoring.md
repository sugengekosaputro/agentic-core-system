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

A preset is a distributable overlay that declares a `coreVersion` and adds skills,
an MCP overlay, commands, and a profile. It must not modify core-managed files
(the engine, the three core skills, the governance region of `AGENTS.md`).

Recommended preset layout:

```
preset-<stack>/
  preset.yaml                 name, version, coreVersion
  skills/stack-<stack>/SKILL.md
  mcp.overlay.json            servers this stack needs (e.g. postgres)
  agents.project.md           text merged into the AGENTS.md project region
  commands.json               e.g. { "verify": "..." }
  profile.yaml                official initializer + Context7 libs + conventions
```

Best practices stay current by fetching official docs via Context7 at scaffold time
rather than freezing framework code in templates.
