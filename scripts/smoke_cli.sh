#!/usr/bin/env bash
set -euo pipefail

# Simple smoke test for CLI before push.
# Runs offline flows using examples/example.json and fails if stderr has warnings/errors.

RED="\033[0;31m"; GREEN="\033[0;32m"; YELLOW="\033[0;33m"; NC="\033[0m"

fail() { echo -e "${RED}Smoke check failed:${NC} $1" >&2; exit 1; }
warns="";

echo "[smoke] Running pytest (fast)"
PYTHONPATH=src python -m pytest -q || fail "pytest failed"

json="examples/example.json"
[[ -f "$json" ]] || fail "Missing offline example JSON at $json"

run_cli() {
  desc="$1"; shift
  echo "[smoke] $desc: jira_issue_console $*"
  set +e
  out=$(python -m jira_issue_console LIC --input "$json" "$@" 2>&1)
  rc=$?
  set -e
  echo "$out" | grep -iE "error|traceback|warning|exception" && warns="${warns}Found warnings/errors for: $desc\n"
  [[ $rc -eq 0 ]] || fail "CLI returned non-zero for $desc"
}

run_cli "CFD export" --cfd /tmp/smoke_cfd.csv
run_cli "Status timing export" --status-timing /tmp/smoke_status_times.csv
run_cli "Transitions export" --transitions /tmp/smoke_transitions.csv

if [[ -n "$warns" ]]; then
  echo -e "${YELLOW}$warns${NC}" >&2
  fail "Warnings or errors detected in CLI output"
fi

echo -e "${GREEN}Smoke CLI passed cleanly${NC}";
