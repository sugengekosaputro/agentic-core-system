# Project Documentation & Artifacts

These folders hold **artifacts** (the documents a project produces), organized by
artifact type. They are outputs, not skills. Reusable methods belong in
`.agents/skills/workflow-*`; technology-specific conventions belong in
`.agents/skills/stack-*`.

## Map: folder and document type

| Folder | Document types | Naming |
|--------|----------------|--------|
| `product/` | PRD, product brief, roadmap | `prd.md` |
| `requirements/` | user stories, acceptance criteria, backlog | `NNN-<feature>.md` |
| `architecture/` | ADRs, design notes, diagrams/ERD | `adr/NNNN-<title>.md` |
| `quality/` | test strategy, plans, QA reports | `NNN-<feature>-testplan.md` |
| `security/` | threat model, security review | `threat-model.md` |
| `operations/` | runbooks, deployment, observability | `runbook-<area>.md` |

## Flow (how artifacts hand off)

```
product/  →  requirements/  →  architecture/  →  code  →  quality/ · security/ · operations/
 (what/why)   (testable behavior)  (how/decisions)  (build)   (verify · harden · run)
```

## Document types, clarified

| Document | Answers | Lives in |
|----------|---------|----------|
| **PRD** | *What* & *why* (product) | `product/` |
| **Requirements / user stories** | Detailed behavior + acceptance criteria | `requirements/` |
| **ADR / design** | *How* (technical decision) | `architecture/adr/` |

Each folder has a `README.md` stating its purpose, document types, and naming
convention.
