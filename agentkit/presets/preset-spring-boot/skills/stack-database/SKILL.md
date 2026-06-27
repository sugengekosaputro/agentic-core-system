---
name: stack-database
description: Manage relational persistence in a Spring Boot app — JPA entities, Spring Data repositories, and Flyway migrations (PostgreSQL). Use for schema changes, entities, indexes, constraints, and migrations.
metadata:
  layer: stack
  sdlc_stage: build
---

# Database (JPA + Flyway + PostgreSQL)

## Method
1. Model JPA entities + Spring Data repositories; keep mapping explicit.
2. Every schema change is a Flyway migration under
   `src/main/resources/db/migration` (`Vn__description.sql`). Never edit an applied
   migration — add a new one.
3. Keep Hibernate `ddl-auto=validate`; the schema is owned by Flyway.
4. Configure the datasource via env (`POSTGRES_URL` / `DB_*`), not committed secrets.
5. Test against a real PostgreSQL. The `postgres` MCP server is available (disabled
   by default; enable it in `.agents/mcp/servers.json` and set `POSTGRES_URL`).

## Use Context7
Fetch current Flyway / Spring Data JPA / PostgreSQL docs via Context7.

## Hand-offs
Application wiring → `stack-springboot`.
