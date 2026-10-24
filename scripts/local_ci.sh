#!/usr/bin/env bash
# Local mirror of the GitHub Actions quality gate.
#
# Runs, in the same order as CI:
#   1. pytest with coverage (90 % gate)
#   2. ruff lint check
#   3. ruff format verification (check only — never rewrites files)
#   4. bandit source scan against src/
#   5. pip-audit dependency audit (network required)
#   6. workflow configuration validation
#
# Prerequisites: a virtual environment with requirements-dev.txt installed
# (created automatically with uv if missing and `uv` is available).
#
# Windows: see README ("Local setup on Windows") for the PowerShell
# equivalent of each step.

set -euo pipefail

cd "$(dirname "$0")/.."

VENV_BIN=".venv/bin"

if [ ! -x "$VENV_BIN/python" ]; then
  echo "No .venv found."
  if command -v uv >/dev/null 2>&1; then
    echo "Creating environment with uv…"
    uv venv --python 3.14 .venv
    uv pip install --python "$VENV_BIN/python" -r requirements-dev.txt
  else
    echo "Create one yourself first:" >&2
    echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt" >&2
    exit 1
  fi
fi

step() {
  printf '\n=== %s ===\n' "$1"
}

step "1/6 pytest (unit + edge cases, coverage >= 90 %)"
"$VENV_BIN/python" -m pytest --cov --cov-report=term-missing --cov-fail-under=90

step "2/6 ruff lint"
"$VENV_BIN/ruff" check .

step "3/6 ruff format verification"
"$VENV_BIN/ruff" format --check .

step "4/6 bandit security scan"
"$VENV_BIN/bandit" -r src -c pyproject.toml --quiet

step "5/6 pip-audit dependency audit"
"$VENV_BIN/pip-audit" --strict

step "6/6 workflow configuration validation"
"$VENV_BIN/python" scripts/validate_workflows.py

printf '\nAll quality-gate checks passed locally. (%s)\n' "$(date -u '+%Y-%m-%d %H:%M:%SZ')"
