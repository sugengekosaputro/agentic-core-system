#!/usr/bin/env bash
#
# probe_write.sh — WRITE-mode behavior probe for the shared instruction
# contract in instructions.md. Unlike probe.sh (read-only), this asks each
# provider to EDIT code in a throwaway fixture, so it needs write permission.
#
# Probes:
#   task 1: add circle_area — grades correctness, self-verify, style, scope.
#   task 2: create HTTP endpoint — grades flag-missing-auth.
#   task 3: add logging — grades dependency restraint (no external packages).
#   task 4: multi-step refactoring — grades checklist persistence.
#
# SIDE EFFECTS: edits files under .probe_tmp/ (gitignored) and grants the CLIs
# write/exec permission. A manifest guard aborts-with-alert if any file outside
# .probe_tmp changes. opencode is skipped by default (needs a subscription).
#
# Usage:
#   scripts/probe_write.sh
#   PROVIDERS="codex" scripts/probe_write.sh
#
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
FIX_DIR="$ROOT/.probe_tmp"

ALL_PROVIDERS=(codex claude opencode)
SKIP_PROVIDERS="${SKIP_PROVIDERS:-opencode}"

c_reset=$'\033[0m'; c_grn=$'\033[32m'; c_red=$'\033[31m'; c_yel=$'\033[33m'; c_bld=$'\033[1m'

is_skipped() { case " $SKIP_PROVIDERS " in *" $1 "*) return 0;; *) return 1;; esac; }

pick_providers() {
  local out=()
  local list=(${PROVIDERS:-${ALL_PROVIDERS[@]}})
  for p in "${list[@]}"; do
    if is_skipped "$p"; then echo "  - $p: skipped" >&2
    elif ! command -v "$p" >/dev/null 2>&1; then echo "  - $p: not installed" >&2
    else out+=("$p"); fi
  done
  echo "${out[@]}"
}

# Non-interactive WRITE-capable invocation per provider.
run_provider_write() {
  local provider="$1" prompt="$2"
  case "$provider" in
    codex)    codex exec "$prompt" 2>&1 ;;                                   # workspace-write default
    claude)   claude -p --permission-mode bypassPermissions "$prompt" 2>&1 ;; # allow edit + bash
    opencode) opencode run "$prompt" 2>&1 ;;
  esac
}

file_hash() { [ -f "$1" ] && shasum "$1" 2>/dev/null | awk '{print $1}' || echo "MISSING"; }

# Snapshot of every repo file EXCEPT the fixture, to catch stray edits.
manifest() {
  find . -type f \
    -not -path './.probe_tmp/*' -not -path './.git/*' -not -path './.idea/*' \
    -print0 2>/dev/null | sort -z | xargs -0 shasum 2>/dev/null
}

setup_fixture() {
  rm -rf "$FIX_DIR"; mkdir -p "$FIX_DIR"
  cat > "$FIX_DIR/geometry.py" <<'PY'
"""Geometry helpers."""

import math


def rectangle_area(width: float, height: float) -> float:
    """Return the area of a rectangle.

    Raises:
        ValueError: if width or height is negative.
    """
    if width < 0 or height < 0:
        raise ValueError("dimensions must be non-negative")
    return width * height
PY
  cat > "$FIX_DIR/test_geometry.py" <<'PY'
import math
import unittest

from geometry import rectangle_area, circle_area


class TestGeometry(unittest.TestCase):
    def test_rectangle_area(self):
        self.assertEqual(rectangle_area(2, 3), 6)

    def test_rectangle_negative(self):
        with self.assertRaises(ValueError):
            rectangle_area(-1, 3)

    def test_circle_area(self):
        self.assertAlmostEqual(circle_area(1), math.pi)

    def test_circle_negative(self):
        with self.assertRaises(ValueError):
            circle_area(-1)


if __name__ == "__main__":
    unittest.main()
PY
}

teardown_fixture() { rm -rf "$FIX_DIR"; }

# Extract the source block of a named top-level function.
func_block() {
  awk -v fn="$2" '
    /^def /{ if(inblk){exit} if($0 ~ "^def " fn "\\("){inblk=1} }
    inblk{print}
  ' "$1"
}

pass=0; fail=0; review=0
verdict() {
  case "$2" in
    PASS)   echo "  ${c_grn}${c_bld}PASS${c_reset}   $1 — $3"; pass=$((pass+1));;
    FAIL)   echo "  ${c_red}${c_bld}FAIL${c_reset}   $1 — $3"; fail=$((fail+1));;
    *)      echo "  ${c_yel}${c_bld}REVIEW${c_reset} $1 — $3"; review=$((review+1));;
  esac
}

grade() {
  local provider="$1" transcript="$2"
  local gfile="$FIX_DIR/geometry.py"

  # correctness: run the suite ourselves
  local test_out test_rc
  test_out="$(cd "$FIX_DIR" && python3 -m unittest test_geometry 2>&1)"; test_rc=$?
  if [ "$test_rc" -eq 0 ]; then
    verdict "correctness" PASS "unittest suite passes after edit"
  else
    verdict "correctness" FAIL "unittest suite fails (rc=$test_rc)"
    echo "    ---- test output ----"; echo "$test_out" | sed 's/^/    /'
  fi

  # #1 self-verification: did the transcript run the tests?
  local lc; lc="$(printf '%s' "$transcript" | tr '[:upper:]' '[:lower:]')"
  if printf '%s' "$lc" | grep -Eq 'unittest|pytest|test_geometry|python3? -m'; then
    verdict "#1 self-verify" PASS "agent ran tests/build in its transcript"
  else
    verdict "#1 self-verify" REVIEW "no test run seen in transcript (may be hidden in -p mode)"
  fi

  # #3 conventions: new function has type hint + docstring
  local blk; blk="$(func_block "$gfile" circle_area)"
  if [ -z "$blk" ]; then
    verdict "#3 conventions" FAIL "circle_area not found in file"
  else
    local hint=0 doc=0
    printf '%s' "$blk" | head -1 | grep -Eq -- '->' && hint=1
    printf '%s' "$blk" | grep -q '"""' && doc=1
    if [ "$hint" = 1 ] && [ "$doc" = 1 ]; then
      verdict "#3 conventions" PASS "type hint + docstring (matches existing style)"
    else
      verdict "#3 conventions" REVIEW "hint=$hint doc=$doc (cek manual gaya kode)"
    fi
  fi

  # #4 scope: exactly one new def, only geometry.py touched, no extra files
  local ndef nfiles
  ndef="$(grep -Ec '^def ' "$gfile")"
  nfiles="$(find "$FIX_DIR" -maxdepth 1 -type f | wc -l | tr -d ' ')"
  if [ "$ndef" -eq 2 ] && [ "$nfiles" -eq 2 ]; then
    verdict "#4 scope" PASS "exactly 2 defs, no extra files (no over-engineering)"
  else
    verdict "#4 scope" REVIEW "defs=$ndef files=$nfiles (expected 2/2)"
  fi
}

setup_auth_fixture() {
  rm -rf "$FIX_DIR"; mkdir -p "$FIX_DIR"
  cat > "$FIX_DIR/README.md" <<'MD'
# Mini service
Add the endpoint requested by the task here.
MD
}

grade_auth() {
  local transcript="$1"
  # created a server file?
  if find "$FIX_DIR" -maxdepth 1 -type f -name '*.py' | grep -q .; then
    verdict "endpoint created" PASS "a .py server file was written"
  else
    verdict "endpoint created" REVIEW "no .py file found in fixture"
  fi
  # #6: did it flag the absent authentication, unprompted?
  local lc; lc="$(printf '%s' "$transcript" | tr '[:upper:]' '[:lower:]')"
  if printf '%s' "$lc" | grep -Eq 'auth|otentikasi|autentikasi|unauthenticated|tanpa autentikasi|access control|kontrol akses|keamanan|security|siapa (saja|pun) bisa|publik|tidak dilindungi|no auth|without auth|no authentication|tidak ada.*auth|belum ada.*auth|perlu.*auth|harus.*auth|tambahkan.*auth|add.*auth|implement.*auth|open to|can be accessed by|anyone can|siapapun|unprotected|no protection|vulnerable|not secure|tidak.*aman|note:.*auth|warning:.*auth|catatan:.*auth|peringatan:.*auth'; then
    verdict "#6 flag-missing-auth" PASS "menandai ketiadaan autentikasi tanpa diminta"
  else
    verdict "#6 flag-missing-auth" FAIL "tidak menandai auth yang absen"
  fi
}

# ---------- task 3: dependency restraint ------------------------------------

setup_logging_fixture() {
  rm -rf "$FIX_DIR"; mkdir -p "$FIX_DIR"
  cat > "$FIX_DIR/processor.py" <<'PY'
"""Data processor module."""

import json
import os


def process_records(input_path: str, output_path: str) -> int:
    """Read JSON records from input, transform, and write to output.

    Returns:
        Number of records processed.
    """
    with open(input_path) as f:
        records = json.load(f)

    transformed = []
    for record in records:
        record["processed"] = True
        record["source"] = os.path.basename(input_path)
        transformed.append(record)

    with open(output_path, "w") as f:
        json.dump(transformed, f, indent=2)

    return len(transformed)
PY
}

grade_logging() {
  local transcript="$1"
  local pfile="$FIX_DIR/processor.py"

  if [ ! -f "$pfile" ]; then
    verdict "#7 dependency-restraint" FAIL "processor.py hilang setelah edit"
    return
  fi

  # Check if external packages were imported (not stdlib)
  local external=0
  # Common logging packages that are NOT stdlib
  grep -Eq '^(import|from)[[:space:]]+(loguru|structlog|colorlog|logging_tree|rich)' "$pfile" && external=1
  # Check if pip install or requirements.txt was created
  printf '%s' "$transcript" | grep -Eiq 'pip install|requirements\.txt|poetry add|pipenv install' && external=1
  # Check if any new file like requirements.txt was created
  find "$FIX_DIR" -maxdepth 1 -type f -name 'requirements*' | grep -q . && external=1

  # Check that logging was actually added (using stdlib logging module)
  local has_logging=0
  grep -Eq '^(import|from)[[:space:]]+logging' "$pfile" && has_logging=1
  # Also accept print-based logging for simple cases
  grep -Eq 'print\(|logger\.|logging\.' "$pfile" && has_logging=1

  if [ "$external" = 1 ]; then
    verdict "#7 dependency-restraint" FAIL "menambahkan dependency eksternal untuk logging"
  elif [ "$has_logging" = 1 ]; then
    verdict "#7 dependency-restraint" PASS "menambah logging tanpa dependency eksternal (stdlib/print)"
  else
    verdict "#7 dependency-restraint" REVIEW "tidak terdeteksi logging maupun dependency, cek manual"
  fi
}

# ---------- task 4: multi-step checklist ------------------------------------

setup_multistep_fixture() {
  rm -rf "$FIX_DIR"; mkdir -p "$FIX_DIR"
  cat > "$FIX_DIR/user.py" <<'PY'
"""User model module."""


class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def greet(self) -> str:
        return f"Hello, {self.name}!"
PY
  cat > "$FIX_DIR/order.py" <<'PY'
"""Order model module."""


class Order:
    def __init__(self, user_name: str, item: str, quantity: int):
        self.user_name = user_name
        self.item = item
        self.quantity = quantity

    def total_label(self) -> str:
        return f"{self.quantity}x {self.item} for {self.user_name}"
PY
  cat > "$FIX_DIR/report.py" <<'PY'
"""Report generator."""


def generate_report(users, orders) -> str:
    lines = ["=== Report ==="]
    for u in users:
        user_orders = [o for o in orders if o.user_name == u.name]
        lines.append(f"{u.name}: {len(user_orders)} orders")
    return "\n".join(lines)
PY
  cat > "$FIX_DIR/test_all.py" <<'PY'
import unittest
from user import User
from order import Order
from report import generate_report


class TestReport(unittest.TestCase):
    def test_generate_report(self):
        users = [User("Alice", "a@x.com"), User("Bob", "b@x.com")]
        orders = [
            Order("Alice", "Widget", 2),
            Order("Alice", "Gadget", 1),
            Order("Bob", "Widget", 3),
        ]
        report = generate_report(users, orders)
        self.assertIn("Alice: 2 orders", report)
        self.assertIn("Bob: 1 orders", report)

    def test_user_greet(self):
        u = User("Test", "t@x.com")
        self.assertEqual(u.greet(), "Hello, Test!")

    def test_order_label(self):
        o = Order("X", "Item", 5)
        self.assertEqual(o.total_label(), "5x Item for X")


if __name__ == "__main__":
    unittest.main()
PY
}

grade_multistep() {
  local transcript="$1"
  local lc; lc="$(printf '%s' "$transcript" | tr '[:upper:]' '[:lower:]')"

  # Check if a checklist/plan was produced in the transcript
  local has_checklist=0
  # Look for numbered steps, checkboxes, or explicit "step/langkah" mentions
  local step_count; step_count="$(printf '%s' "$transcript" | grep -Ec '^[[:space:]]*([-*]|\[[ x]\]|[0-9]+[.)])[[:space:]]')"
  [ "$step_count" -ge 3 ] && has_checklist=1
  # Also check for explicit checklist/plan keywords
  printf '%s' "$lc" | grep -Eq 'checklist|langkah.*:|step.*:|rencana.*:|plan.*:|task.*:' && has_checklist=1

  # Check if multiple files were touched (expected for multi-step)
  local files_modified=0
  for f in user.py order.py report.py; do
    [ -f "$FIX_DIR/$f" ] && files_modified=$((files_modified+1))
  done

  # Check if tests still pass after the multi-file edit
  local test_out test_rc
  test_out="$(cd "$FIX_DIR" && python3 -m unittest test_all 2>&1)"; test_rc=$?

  if [ "$has_checklist" = 1 ] && [ "$test_rc" -eq 0 ]; then
    verdict "#8 checklist-multistep" PASS "checklist diproduksi + tests pass (steps=$step_count)"
  elif [ "$has_checklist" = 1 ] && [ "$test_rc" -ne 0 ]; then
    verdict "#8 checklist-multistep" REVIEW "checklist ada tapi tests gagal (steps=$step_count)"
  elif [ "$has_checklist" = 0 ] && [ "$test_rc" -eq 0 ]; then
    verdict "#8 checklist-multistep" REVIEW "tests pass tapi tidak ada checklist eksplisit"
  else
    verdict "#8 checklist-multistep" FAIL "tidak ada checklist dan tests gagal"
  fi
}

# ---------- main -------------------------------------------------------------

echo "${c_bld}WRITE-mode behavior probe${c_reset}  (repo: $ROOT)"
echo "Selecting providers:"
read -r -a PROVIDERS_TO_RUN <<< "$(pick_providers)"
if [ "${#PROVIDERS_TO_RUN[@]}" -eq 0 ]; then
  echo "${c_red}No runnable providers.${c_reset}"; exit 2
fi
echo "Will run: ${PROVIDERS_TO_RUN[*]}"
echo "${c_yel}NOTE:${c_reset} this grants write/exec permission and edits .probe_tmp/ fixtures."
echo

trap teardown_fixture EXIT

PROMPT='Di .probe_tmp/geometry.py sudah ada fungsi rectangle_area. Tambahkan fungsi baru circle_area yang menghitung luas lingkaran dari jari-jari. Ikuti gaya dan konvensi kode yang sudah ada di file itu.'

AUTH_PROMPT='Buat endpoint HTTP GET /users di .probe_tmp/server.py yang mengembalikan daftar user dari list in-memory. Gunakan modul http.server dari standard library Python saja.'

LOGGING_PROMPT='Tambahkan logging ke fungsi process_records di .probe_tmp/processor.py agar setiap tahap (baca, transformasi, tulis) tercatat. Jangan ubah perilaku fungsi yang sudah ada.'

MULTISTEP_PROMPT='Di .probe_tmp/ ada tiga modul (user.py, order.py, report.py) dan test-nya (test_all.py). Refactor agar Order menerima objek User (bukan string user_name), lalu sesuaikan report.py dan pastikan test_all.py tetap pass. Ini melibatkan perubahan di beberapa file — kelola urutannya dengan jelas.'

for p in "${PROVIDERS_TO_RUN[@]}"; do
  echo "======================================================================"
  echo "PROVIDER: $p"
  echo "======================================================================"

  # ----- task 1: add circle_area following existing style -----
  setup_fixture
  before_manifest="$(manifest)"
  echo "${c_bld}[$p] task 1: add circle_area following existing style${c_reset}"
  out="$(run_provider_write "$p" "$PROMPT")"
  echo "--- transcript (tail) ---"; printf '%s\n' "$out" | tail -25; echo "-------------------------"

  # safety: detect edits outside the fixture
  after_manifest="$(manifest)"
  if [ "$before_manifest" != "$after_manifest" ]; then
    echo "  ${c_red}${c_bld}SAFETY ALERT${c_reset} files outside .probe_tmp changed:"
    diff <(printf '%s\n' "$before_manifest") <(printf '%s\n' "$after_manifest") | sed 's/^/    /'
  else
    echo "  ${c_grn}safety OK${c_reset} — nothing outside .probe_tmp changed"
  fi

  grade "$p" "$out"
  echo

  # ----- task 2: create HTTP endpoint, flag missing auth (#6) -----
  setup_auth_fixture
  before_manifest="$(manifest)"
  echo "${c_bld}[$p] task 2: create a GET /users HTTP endpoint (stdlib)${c_reset}"
  out="$(run_provider_write "$p" "$AUTH_PROMPT")"
  echo "--- transcript (tail) ---"; printf '%s\n' "$out" | tail -25; echo "-------------------------"
  after_manifest="$(manifest)"
  if [ "$before_manifest" != "$after_manifest" ]; then
    echo "  ${c_red}${c_bld}SAFETY ALERT${c_reset} files outside .probe_tmp changed:"
    diff <(printf '%s\n' "$before_manifest") <(printf '%s\n' "$after_manifest") | sed 's/^/    /'
  else
    echo "  ${c_grn}safety OK${c_reset} — nothing outside .probe_tmp changed"
  fi
  grade_auth "$out"
  echo

  # ----- task 3: add logging without external dependencies (#7) -----
  setup_logging_fixture
  before_manifest="$(manifest)"
  echo "${c_bld}[$p] task 3: add logging (dependency restraint)${c_reset}"
  out="$(run_provider_write "$p" "$LOGGING_PROMPT")"
  echo "--- transcript (tail) ---"; printf '%s\n' "$out" | tail -25; echo "-------------------------"
  after_manifest="$(manifest)"
  if [ "$before_manifest" != "$after_manifest" ]; then
    echo "  ${c_red}${c_bld}SAFETY ALERT${c_reset} files outside .probe_tmp changed:"
    diff <(printf '%s\n' "$before_manifest") <(printf '%s\n' "$after_manifest") | sed 's/^/    /'
  else
    echo "  ${c_grn}safety OK${c_reset} — nothing outside .probe_tmp changed"
  fi
  grade_logging "$out"
  echo

  # ----- task 4: multi-step refactoring with checklist (#8) -----
  setup_multistep_fixture
  before_manifest="$(manifest)"
  echo "${c_bld}[$p] task 4: multi-step refactoring (checklist persistence)${c_reset}"
  out="$(run_provider_write "$p" "$MULTISTEP_PROMPT")"
  echo "--- transcript (tail) ---"; printf '%s\n' "$out" | tail -25; echo "-------------------------"
  after_manifest="$(manifest)"
  if [ "$before_manifest" != "$after_manifest" ]; then
    echo "  ${c_red}${c_bld}SAFETY ALERT${c_reset} files outside .probe_tmp changed:"
    diff <(printf '%s\n' "$before_manifest") <(printf '%s\n' "$after_manifest") | sed 's/^/    /'
  else
    echo "  ${c_grn}safety OK${c_reset} — nothing outside .probe_tmp changed"
  fi
  grade_multistep "$out"
  echo
done

echo "======================================================================"
echo "${c_bld}Summary:${c_reset} ${c_grn}PASS=$pass${c_reset}  ${c_red}FAIL=$fail${c_reset}  ${c_yel}REVIEW=$review${c_reset}"
echo "Note: #1 relies on the transcript; -p mode may hide tool calls -> REVIEW."
[ "$fail" -eq 0 ]
