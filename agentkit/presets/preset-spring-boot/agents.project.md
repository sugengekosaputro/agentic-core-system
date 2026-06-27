## Project Guidance (Spring Boot)

A Spring Boot (Maven) project. Conventions live in
`.agents/skills/stack-springboot/` and `.agents/skills/stack-database/`. Build and
test with `./mvnw`. Keep the web layering controller → service → repository; schema
changes go through Flyway migrations; configuration uses environment variables
(`.env`), never committed secrets.
