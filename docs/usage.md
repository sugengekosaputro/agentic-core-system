# Usage — a complete beginner's guide

This guide takes you from a fresh machine to using agentkit in your own projects,
explaining each step (not just commands). agentkit is a small **Python**
command-line tool. You install it once; then you run it inside any project, and it
sets up that project's AI-agent context for you.

> You do **not** copy this repository into your project. The tool lives on your
> machine; only its output (a `.agents/` folder + per-provider files) is written
> into your project, which then stands on its own.

---

## What you will end up with

After setup you will have a command called `agentkit`. Inside any project you can run:

- `agentkit init` — set up agent context for the project (once).
- `agentkit sync` — regenerate the per-provider files after you change the source.
- `agentkit validate` — check everything is consistent.
- `agentkit upgrade` — pull in newer kit files later.

---

## Requirements

| Requirement | Why | Minimum |
|-------------|-----|---------|
| **Python** | agentkit is written in Python | 3.10 or newer |
| **git** | hooks + version control of your project | any recent version |
| **pipx** | installs Python command-line tools cleanly (isolated) | latest |

Check what you already have:

```sh
python3 --version     # expect: Python 3.10.x or higher
git --version         # any version is fine
```

If `python3` is missing or older than 3.10, do **Step 1**. Otherwise skip to Step 2.

---

## Step 1 — Install Python 3.10+ (only if needed)

Python is the language agentkit runs on. Install it for your operating system:

- **macOS** — easiest with [Homebrew](https://brew.sh):
  ```sh
  brew install python
  ```
  Or download the installer from <https://www.python.org/downloads/>.
- **Windows** — download from <https://www.python.org/downloads/> and, in the
  installer, tick **"Add python.exe to PATH"**. Or: `winget install Python.Python.3.12`.
- **Linux (Debian/Ubuntu)**:
  ```sh
  sudo apt update && sudo apt install -y python3 python3-venv python3-pip
  ```

Verify:

```sh
python3 --version
```

---

## Step 2 — Install pipx

**What is pipx?** Plain `pip install` can clash with your system Python, and modern
systems often block it (the "externally-managed environment" / PEP 668 error). pipx
solves this: it installs each command-line tool in its own private environment and
puts the command on your PATH, so `agentkit` "just works" without breaking anything.

Install pipx:

- **macOS**: `brew install pipx`
- **Windows**: `python -m pip install --user pipx`
- **Linux**: `sudo apt install -y pipx`  (or `python3 -m pip install --user pipx`)

Then let pipx fix your PATH and **open a new terminal afterward**:

```sh
pipx ensurepath
```

---

## Step 3 — Install agentkit

agentkit is not yet on PyPI, so you install it from the source repository. Pick the
option that matches your situation:

**A) From GitHub (recommended once the repo is pushed):**
```sh
pipx install git+https://github.com/sugengekosaputro/agentic-core-system.git
```

**B) From a local clone (works today):**
```sh
git clone https://github.com/sugengekosaputro/agentic-core-system.git
pipx install ./agentic-core-system
```

**C) Later, once published to PyPI:**
```sh
pipx install agentkit-core
```

Verify the command is available:

```sh
agentkit --version        # expect: agentkit 0.1.0
```

If you get "command not found", see [Troubleshooting](#troubleshooting).

---

## Step 4 — Use it in a brand-new (blank) project

```sh
mkdir my-app           # create your project folder
cd my-app
git init               # agentkit's hooks live in git
agentkit init          # set up the agent context
```

`agentkit init` creates, in `my-app/`:

- `.agents/` — the **canonical source** you edit: `permissions.json`, `mcp/servers.json`,
  `README.md`, `project.json`, and `skills/` (the core skills core-init,
  core-consultant, core-orchestrator).
- `AGENTS.md` — the top-level instruction file every provider reads.
- Generated provider files (do **not** edit these by hand): `.kiro/`, `.claude/` +
  `CLAUDE.md`, `.codex/`, `opencode.json`, `.antigravity/`, `.mcp.json`.
- `docs/` — a documentation skeleton organized by job function.
- `.githooks/` — checks that run automatically when you commit/push.

Then build your actual application with its normal tool — agentkit does not generate
app code. For example: Spring Boot via [Spring Initializr](https://start.spring.io),
Angular via `ng new`, a Python app via your usual scaffolder.

---

## Step 5 — Use it in an existing project

```sh
cd my-existing-project
agentkit init          # safe: it never overwrites files you already have
agentkit validate
```

`init` is idempotent — running it again changes nothing it has already created. If
your project already has scattered AI config (a `CLAUDE.md`, a `.cursor/` folder,
ad-hoc MCP settings), ask your agent to follow the `core-init` skill, which guides
auditing and folding those into the canonical `.agents/` (it will not delete
anything without your approval).

---

## The daily loop

The golden rule: **edit the source, never the generated files.**

```sh
# 1. Edit only AGENTS.md or anything under .agents/
#    (e.g. add a skill, change a permission, add an MCP server)

# 2. Regenerate the per-provider files from your edits:
agentkit sync

# 3. Check everything is consistent:
agentkit validate

# 4. Commit. A git hook re-runs the check and blocks the commit if something drifted.
git add -A && git commit -m "..."
```

Why this matters: each AI provider (Kiro, Claude, Codex, opencode, Antigravity)
wants its config in a different place/format. You maintain **one** source; agentkit
keeps all the provider files correct and in sync.

---

## Optional — the manifest (`agentkit.yaml`)

If you create an `agentkit.yaml` file **before** running `agentkit init`, setup
becomes fully automatic (no questions asked). Minimal example:

```yaml
project:
  name: my-app
  language: java          # optional
  framework: spring-boot  # optional
  commands:
    verify: ""            # a command to run before "git push", e.g. "./mvnw test"
memory:
  scope: both
```

Without a manifest, `init` fills in sensible defaults based on the folder name.

---

## Updating agentkit later

```sh
pipx upgrade agentkit-core      # get the newer tool
cd my-app && agentkit upgrade   # refresh only the kit-managed files
```

`upgrade` refreshes the parts owned by the kit (the core skills, `.agents/README.md`,
and the git hooks) and re-syncs the provider files. It leaves **your** content alone
(your permissions, your `AGENTS.md` project section, your docs). Review the changes
it reports, then commit.

---

## Uninstall

```sh
pipx uninstall agentkit-core
```

This removes the tool. Files already written into your projects stay (they are
yours and self-contained).

---

## Command reference

| Command | What it does |
|---------|--------------|
| `agentkit init` | bootstrap a blank project or adapt an existing one |
| `agentkit sync` | regenerate provider files from `.agents` (add `--check` to verify only) |
| `agentkit validate` | validate the canonical source and that provider files are in sync |
| `agentkit upgrade` | refresh kit-managed files to the installed version |

---

## Troubleshooting

**`agentkit: command not found`**
pipx put the command in a folder that is not on your PATH yet. Run
`pipx ensurepath`, then **close and reopen your terminal**. On macOS/Linux the
folder is usually `~/.local/bin`.

**`error: externally-managed-environment` (PEP 668)**
You tried `pip install` directly. Use **pipx** instead (Step 2) — that is exactly
what pipx is for.

**`python3: command not found` or version below 3.10**
Do Step 1. On Windows the command may be `python` instead of `python3`.

**`git: command not found`**
Install git: macOS `brew install git`, Debian/Ubuntu `sudo apt install git`,
Windows <https://git-scm.com/download/win>.

**A commit is blocked by the pre-commit hook**
That means the generated files drifted from your edits. Run `agentkit sync`, then
`git add -A` and commit again.

**Behind a corporate proxy / no internet**
pipx needs network access to install. Configure your proxy (e.g. `HTTPS_PROXY`) or
install on a connected machine.
