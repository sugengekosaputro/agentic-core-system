#!/usr/bin/env bash
#
# check_adapters.sh — static validation for provider adapter pointers.
#
# This script does not run provider CLIs. It only verifies that each adapter
# still delegates to instructions.md using the syntax this template expects.
#
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

c_reset=$'\033[0m'
c_grn=$'\033[32m'
c_red=$'\033[31m'
c_bld=$'\033[1m'

failures=0

pass() {
  echo "  ${c_grn}${c_bld}PASS${c_reset} $1"
}

fail() {
  echo "  ${c_red}${c_bld}FAIL${c_reset} $1"
  failures=$((failures + 1))
}

require_file() {
  local label="$1" path="$2"
  if [ -f "$path" ]; then
    pass "$label"
  else
    fail "$label (missing $path)"
  fi
}

require_grep() {
  local label="$1" path="$2" pattern="$3"
  if [ ! -f "$path" ]; then
    fail "$label (missing $path)"
  elif grep -Eq "$pattern" "$path"; then
    pass "$label"
  else
    fail "$label"
  fi
}

require_fixed() {
  local label="$1" path="$2" text="$3"
  if [ ! -f "$path" ]; then
    fail "$label (missing $path)"
  elif grep -Fq "$text" "$path"; then
    pass "$label"
  else
    fail "$label"
  fi
}

require_absent_grep() {
  local label="$1" path="$2" pattern="$3"
  if [ ! -f "$path" ]; then
    fail "$label (missing $path)"
  elif grep -Eq "$pattern" "$path"; then
    fail "$label"
  else
    pass "$label"
  fi
}

require_max_lines() {
  local label="$1" path="$2" max_lines="$3"
  local line_count
  if [ ! -f "$path" ]; then
    fail "$label (missing $path)"
    return
  fi
  line_count="$(wc -l < "$path" | tr -d ' ')"
  if [ "$line_count" -le "$max_lines" ]; then
    pass "$label"
  else
    fail "$label ($line_count lines > $max_lines)"
  fi
}

echo "${c_bld}Static adapter validation${c_reset} (repo: $ROOT)"

require_file "shared instructions file exists" "instructions.md"
require_fixed "AGENTS.md delegates to instructions.md" "AGENTS.md" "[instructions.md](instructions.md)"
require_grep "CLAUDE.md imports @instructions.md" "CLAUDE.md" '^@instructions\.md[[:space:]]*$'
require_grep "opencode.json registers instructions.md" "opencode.json" '"instructions"[[:space:]]*:[[:space:]]*\[[[:space:]]*"instructions\.md"[[:space:]]*\]'
require_grep ".codex/config.toml has instructions fallback" ".codex/config.toml" '^project_doc_fallback_filenames[[:space:]]*=[[:space:]]*\[[[:space:]]*"instructions\.md"[[:space:]]*\][[:space:]]*$'

require_max_lines "AGENTS.md stays pointer-only sized" "AGENTS.md" 20
require_max_lines "CLAUDE.md stays pointer-only sized" "CLAUDE.md" 20
require_max_lines "opencode.json stays adapter-sized" "opencode.json" 20
require_max_lines ".codex/config.toml stays adapter-sized" ".codex/config.toml" 20

require_absent_grep "AGENTS.md has no duplicated guidance sections" "AGENTS.md" '^#{2,}[[:space:]]'
require_absent_grep "CLAUDE.md has no duplicated guidance sections" "CLAUDE.md" '^#{2,}[[:space:]]'

require_absent_grep "instructions.md has no provider-specific adapter details" "instructions.md" '(^|[^[:alnum:]_])(Codex|Claude|opencode|CLAUDE\.md|opencode\.json|project_doc_fallback_filenames|@instructions\.md|\.codex)([^[:alnum:]_]|$)'

if [ "$failures" -eq 0 ]; then
  echo "${c_grn}${c_bld}All adapter checks passed.${c_reset}"
  exit 0
fi

echo "${c_red}${c_bld}$failures adapter check(s) failed.${c_reset}"
exit 1
