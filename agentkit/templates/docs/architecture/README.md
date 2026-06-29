# Architecture

- **Purpose:** Record *how* the system is built and *why* technical choices were
  made, after product and requirements are understood.
- **Document types:** `adr/` (Architecture Decision Records) + index; `design/`
  (optional notes, diagrams, ERDs).
- **Naming:** `adr/NNNN-<short-title>.md` (zero-padded, monotonic, never reused).
- **Inputs / outputs:** reads `requirements/`; produces ADRs consumed during
  implementation.

Start an ADR from `adr/template.md` and add it to `adr/README.md`.
