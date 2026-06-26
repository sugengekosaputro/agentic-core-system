#!/usr/bin/env node
"use strict";

// Thin wrapper: agentkit's logic lives in the Python package (single source of
// truth). This shim locates Python, ensures the package is importable (installing
// it on first run if needed), then forwards all arguments to `agentkit.cli`.

const { spawnSync } = require("child_process");

const args = process.argv.slice(2);

function run(cmd, cmdArgs, opts) {
  return spawnSync(cmd, cmdArgs, Object.assign({ stdio: "inherit" }, opts || {}));
}

for (const py of ["python3", "python"]) {
  const probe = spawnSync(py, ["-c", "import agentkit"], { stdio: "ignore" });
  if (probe.error) {
    continue; // this interpreter is not available; try the next
  }
  if (probe.status !== 0) {
    console.error("agentkit: installing agentkit-core (first run)...");
    run(py, ["-m", "pip", "install", "--quiet", "--user", "agentkit-core"]);
  }
  const result = run(py, ["-m", "agentkit.cli", ...args]);
  process.exit(result.status === null ? 1 : result.status);
}

console.error(
  "agentkit (npx) requires Python 3.10+. Install Python, or use: pipx install agentkit-core"
);
process.exit(127);
