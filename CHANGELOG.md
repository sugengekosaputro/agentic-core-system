# Changelog

All notable changes to agentkit-core are documented here. This project follows
[Semantic Versioning](https://semver.org/) and
[Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- Initial extraction of the agent-context engine from the springboot-starter
  prototype: canonical `.agents` → generated provider adapters.
- Layered Core / Preset / Manifest architecture (see `docs/`).
- Three core skills: `core-init`, `core-consultant`, `core-orchestrator`.
- CLI: `agentkit init | validate | upgrade | sync` (Python/pipx + npx wrapper).
