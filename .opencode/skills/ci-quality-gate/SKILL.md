---
name: ci-quality-gate
description: github-ci-quality-gate work (merge quality gate: pytest/Ruff/Bandit/pip-audit/CodeQL + workflow validator). Use for ANY task under /home/fabiljayson/Projects/github-ci-quality-gate — covers local CI mirror, the do-not-weaken rule and pinning conventions.
---

# github-ci-quality-gate

Merge quality gate for PRs to `main`: 4 parallel CI jobs (pytest matrix 3.12–3.14 with ≥ 90 % coverage across 78 tests, `ruff check` + `ruff format --check`, Bandit + pip-audit strict, workflow-file validation) plus a separate `codeql.yml`. Enforcement comes from the `protect-main` ruleset (6 required checks, no bypass).

## The one invariant: never weaken the gate

- Ruff runs with `check` + `format --check` — **verify only, never auto-fix** in CI.
- Third-party actions stay pinned to **full commit SHA** with timeouts and least-privilege permissions.
- Test/demo package `quality_gate_demo` is intentionally tiny — the interesting part is the pipeline; don't inflate the demo.
- pip-audit runs `--strict`; dev dependency versions are frozen in `requirements-dev.txt` (pip freeze).

## Commands

```bash
cd github-ci-quality-gate
.venv/bin/pytest                          # 78 tests, 100 % coverage
bash scripts/local_ci.sh                  # full local mirror of the gate (6 steps)
python scripts/validate_workflows.py      # SHA/timeout/permission/fork-unsafe validation
```

## Pitfalls (documented)

- `git -c key=val` needs a command after it; `git revert --no-edit` goes BEFORE `HEAD`.
- PyYAML reads unquoted `on:` as boolean True (handled inside the validator — keep it that way).
- Demo runs showed the full red→green cycle: a witness run F401 failed the Ruff job and was reverted (`40111778596` → `40111893562` → `40112008475`).
