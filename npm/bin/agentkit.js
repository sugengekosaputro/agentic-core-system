#!/usr/bin/env node
"use strict";

// Thin wrapper: agentkit's logic lives in the Python package (single source of
// truth). This shim locates a Python with `agentkit` importable and forwards all
// arguments to `agentkit.cli`. It does NOT auto-install (system Python is often
// externally managed / PEP 668); instead it prints precise install guidance.

const { spawnSync } = require("child_process");

const args = process.argv.slice(2);

for (const py of ["python3", "python"]) {
  const probe = spawnSync(py, ["-c", "import agentkit"], { stdio: "ignore" });
  if (probe.error) {
    continue; // this interpreter is not available; try the next
  }
  if (probe.status === 0) {
    const result = spawnSync(py, ["-m", "agentkit.cli", ...args], { stdio: "inherit" });
    process.exit(result.status === null ? 1 : result.status);
  }
}

console.error(
  [
    "agentkit (npx) needs the Python engine installed (agentkit-core).",
    "Install it with pipx (PEP 668 friendly), then re-run `npx agentkit <command>`:",
    "  pipx install agentkit-core                            # once published to PyPI",
    "  pipx install /path/to/agentic-core-system             # from a local clone",
    "  pipx install git+https://github.com/<you>/agentic-core-system.git   # from GitHub",
  ].join("\n")
);
process.exit(127);
