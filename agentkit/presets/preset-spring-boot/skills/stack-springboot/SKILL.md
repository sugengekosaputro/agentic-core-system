---
name: stack-springboot
description: Conventions for a Spring Boot (Maven) application — controllers, services, DTOs, configuration, and verification. Use for feature work, refactors, dependency changes, and running tests in a Spring Boot project.
metadata:
  layer: stack
  sdlc_stage: build
---

# Spring Boot conventions

## Method
1. Layer the code: controller (web) → service (logic) → repository (data). Keep
   controllers thin.
2. Use constructor injection. Expose DTOs at the web layer, not JPA entities.
3. Configure via `application.yaml` + environment variables (`.env`); no secrets in code.
4. Add tests (JUnit + Spring Boot Test; `@WebMvcTest`, `@DataJpaTest` as fits).
5. Verify with the project's command (`.agents/project.json` `commands.verify`),
   e.g. `./mvnw test`.

## Use Context7
Fetch current Spring Boot / Spring docs via Context7 before relying on memory.

## Hand-offs
Schema/persistence → `stack-database`. Pair with any installed `workflow-*` skill
for project-specific delivery method.
