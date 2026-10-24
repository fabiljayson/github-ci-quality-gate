# Architecture

## Overview

The project is a **quality gate**: a small Python package that must pass
an automated review pipeline before changes reach `main`. The package is
deliberately tiny; the durable value is the pipeline around it.

```text
                ┌────────────────────── trigger ──────────────────────┐
                │  pull_request → main | push → main | workflow_dispatch │
                └───────────────────────┬─────────────────────────────┘
                                        ▼
                    ┌────────────────────  CI  ────────────────────┐
                    │                                              │
   Tests (3.12/3.13/3.14)   Code quality   Security   Workflow validation
   pytest + coverage 90 %   ruff check     bandit     scripts/
   junit + coverage xml     format check   pip-audit  validate_workflows.py
   artifacts (5 d)          pinned ruff    SARIF-less JSON artifact
                    └───────────────────────┬──────────────────────┘
                                            ▼
                       repository rules (branch protection)
                          required status checks → merge allowed
```

`codeql.yml` runs separately (pull requests, pushes to `main`, and a
weekly cron) and writes its results to the repository **Security** tab.

## Trigger map

| Event | ci.yml | codeql.yml |
|---|---|---|
| `pull_request` → `main` | yes | yes |
| `push` → `main` | yes | yes |
| Pull request from a fork | runs with read-only token, no secrets | yes |
| `workflow_dispatch` | yes | no |
| Weekly schedule | no | Mondays 05:17 UTC |

Deliberately **not** used: `pull_request_target` (runs fork code with
privileged access) — see `docs/security.md`.

## Job inventory (exact names used by branch protection)

Required status checks are keyed by these job *names* (as GitHub displays
them), not by file or `job_id`:

| Displayed job name | Job id | Layer | Timeout |
|---|---|---|---|
| `Tests (Python 3.12)` / `(3.13)` / `(3.14)` | tests | execution | 10 min |
| `Code quality (Ruff)` | quality | lint/format | 5 min |
| `Security (Bandit + pip-audit)` | security | dependencies | 10 min |
| `Workflow validation` | workflow-validation | configuration | 5 min |

The four jobs are independent and run **in parallel**; no redundant
installation happens between them. Every job sets its own
`timeout-minutes` so a hung step cannot consume the 6-hour default.

## Failure propagation

- pytest exits non-zero on test failure **or** coverage below 90 %
  (`--cov-fail-under=90`).
- `ruff check .` exits non-zero on lint violations; `ruff format --check`
  exits non-zero if any file would be reformatted (CI never mutates code).
- `bandit` exits non-zero when findings exist (severity/info levels);
  `pip-audit --strict` fails on known CVEs **and** on resolve/input errors,
  so a network failure cannot silently yield a green build.
- `scripts/validate_workflows.py` exits 1 listing each policy violation.
- GitHub captures each job's exit code; a failed job fails the run and —
  once required in repository rules — blocks the merge.

## Dependency flow

All tooling versions are **pinned** in `requirements-dev.txt`
(`pip freeze` output), committed to git:

- `ci.yml` installs it: `python -m pip install -r requirements-dev.txt`.
- `quality` and `workflow-validation` jobs re-declare the single tool they
  need (`ruff==0.17.2`, `pyyaml==6.0.3`) for a fast cold start.
- pip-audit scans the environment installed from that same file, so the
  audit covers **exactly** what CI executes.
- The runtime package `quality_gate_demo` has zero dependencies.

Third-party GitHub Actions are pinned to full 40-character commit SHAs
(the strongest available protection against tag-rewriting supply-chain
attacks), with the release noted as an inline comment.

## Concurrency and cost control

- One run per (branch, event) at a time: `concurrency` cancels superseded
  pull-request runs; push/dispatch runs are not cancelled mid-flight.
- pip cache (via `setup-python`, keyed on `requirements-dev.txt`) and
  loose job timeouts keep wall-clock time low; the full gate is designed
  to finish in well under 3 minutes.
- Artifacts are uploaded with `if: always()` (diagnosing failures costs
  nothing extra) and expire after 5 days.
