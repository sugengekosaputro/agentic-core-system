# Contributing to agentkit-core

Thanks for helping improve the kit. Pick the guide that matches what you're doing:

- **Developing the core** (engine, templates, presets) → [docs/development.md](docs/development.md)
- **Building a preset or skill** on top of core → [docs/authoring.md](docs/authoring.md)
- **Using** agentkit in your own project → [docs/usage.md](docs/usage.md)

Before opening a PR: run `python3 -m unittest discover -s tests` and make sure
`agentkit validate` is green in a smoke `init`.
