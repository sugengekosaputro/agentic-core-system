# Requirements

- **Virtual Assistant:** Business Analyst (`virtual-assistant-business-analyst`)
- **Purpose:** Break product intent (`product/`) into concrete, testable behavior:
  user stories, acceptance criteria, prioritized backlog.
- **Document types:** user stories, acceptance criteria, backlog notes.
- **Naming:** `NNN-<feature>.md` (e.g. `010-user-login.md`).
- **Inputs / outputs:** reads `product/`; feeds `architecture/`.

Each story is independently testable with explicit acceptance criteria so QA can
verify it later.
