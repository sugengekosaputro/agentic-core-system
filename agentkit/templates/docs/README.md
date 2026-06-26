# Project Documentation & Artifacts

These folders hold **artifacts** (the documents a project produces), organized by
**virtual assistant** (the job function responsible) at the top level and
**document type** inside. They are outputs, not skills — the methodology that
produces them lives in `.agents/skills/virtual-assistant-*`.

## Map: virtual assistant × folder × document type

| Folder | Virtual Assistant (skill) | Document types | Naming |
|--------|---------------------------|----------------|--------|
| `product/` | `virtual-assistant-product-manager` | PRD, product brief, roadmap | `prd.md` |
| `requirements/` | `virtual-assistant-business-analyst` | user stories, acceptance criteria, backlog | `NNN-<feature>.md` |
| `architecture/` | `virtual-assistant-architect` | ADRs, design notes, diagrams/ERD | `adr/NNNN-<title>.md` |
| `quality/` | `virtual-assistant-qa` *(reserved)* | test strategy, plans, QA reports | `NNN-<feature>-testplan.md` |
| `security/` | `virtual-assistant-security` *(reserved)* | threat model, security review | `threat-model.md` |
| `operations/` | `virtual-assistant-devops` *(reserved)* | runbooks, deployment, observability | `runbook-<area>.md` |

## Flow (how artifacts hand off)

```
product/  →  requirements/  →  architecture/  →  code  →  quality/ · security/ · operations/
 (what/why)   (testable behavior)  (how/decisions)  (build)   (verify · harden · run)
```

## Document types, clarified

| Document | Answers | Virtual Assistant | Lives in |
|----------|---------|-------------------|----------|
| **PRD** | *What* & *why* (product) | Product Manager | `product/` |
| **Requirements / user stories** | Detailed behavior + acceptance criteria | Business Analyst | `requirements/` |
| **ADR / design** | *How* (technical decision) | Architect | `architecture/adr/` |

Each folder has a `README.md` stating its virtual assistant, purpose, document
types, and naming convention.
