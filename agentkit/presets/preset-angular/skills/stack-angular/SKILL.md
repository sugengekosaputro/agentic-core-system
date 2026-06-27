---
name: stack-angular
description: Conventions for an Angular (TypeScript) frontend — components, services, routing, state, and testing. Use for UI feature work, refactors, and dependency changes in an Angular project.
metadata:
  layer: stack
  sdlc_stage: build
---

# Angular conventions

## Method
1. Structure by feature (standalone components or feature modules). Keep components
   presentational; push logic into services.
2. Use dependency injection; type everything (avoid `any`); use the async pipe for
   observables.
3. Route with the Angular Router; lazy-load feature routes.
4. Manage state explicitly (services/signals, or a chosen store).
5. Lint and test (Jasmine/Karma or Jest); verify with the project's command
   (`.agents/project.json` `commands.verify`), e.g. `npm run build`.

## Use Context7
Fetch current Angular / RxJS / TypeScript docs via Context7 before relying on memory.

## Hand-offs
General method → `virtual-assistant-developer`.
