# github-ci-quality-gate

An automatically enforced **merge quality gate** for GitHub pull requests:
every change to `main` must pass tests, linting, formatting, and two
independent security scans — or the PR simply cannot be merged.

[![CI](https://github.com/fabiljayson/github-ci-quality-gate/actions/workflows/ci.yml/badge.svg)](https://github.com/fabiljayson/github-ci-quality-gate/actions/workflows/ci.yml)
[![CodeQL](https://github.com/fabiljayson/github-ci-quality-gate/actions/workflows/codeql.yml/badge.svg)](https://github.com/fabiljayson/github-ci-quality-gate/actions/workflows/codeql.yml)

Built as a complete, production-minded educational project (DevOps / CI-CD
/ software QA). The Python package inside is intentionally tiny —
`quality_gate_demo` — so the interesting part is the **pipeline** around it,
not the package itself.

## Objectives

1. Run automatically on every pull request to `main`, on pushes to `main`,
   and on demand (`workflow_dispatch`).
2. Execute unit/edge-case tests with pytest across a Python version matrix.
3. Enforce linting and formatting with Ruff (verify — never auto-fix).
4. Scan source code with Bandit, dependencies with pip-audit,
   and code with CodeQL.
5. Validate the workflow files themselves (pinned actions, timeouts,
   least-privilege permissions, no fork-unsafe events).
6. Provide actionable failure output and 5-day diagnostic artifacts.
7. Block merges when required checks fail (repository rules).
8. Mirror the whole gate locally with a single script.

## Workflow at a glance

Four parallel jobs (see `.github/workflows/ci.yml`):

| Job | What it does | Enforces |
|---|---|---|
| `Tests (Python 3.12 / 3.13 / 3.14)` | pytest + coverage | ≥ 90 % coverage, 78 tests green |
| `Code quality (Ruff)` | `ruff check .` + `ruff format --check` | lint & formatting |
| `Security (Bandit + pip-audit)` | source scan + dependency CVE audit | exit-code strict |
| `Workflow validation` | `scripts/validate_workflows.py` | SHA-pinned actions, timeouts, permissions |

Plus a separate `codeql.yml` (results in the repository *Security* tab).

A green workflow alone does **not** block a merge — enforcement requires
the repository rules described below under *Branch protection setup*.

## Technology stack

- **CI:** GitHub Actions (`pull_request` + `push` + manual triggers)
- **Language:** Python 3.12–3.14 (matrix), typed throughout
- **Tests:** pytest, pytest-cov (junit + coverage XML artifacts)
- **Lint/format:** Ruff (`check` + `format --check`)
- **Security:** Bandit, pip-audit (`--strict`), GitHub CodeQL
- **Pinning:** every third-party action referenced by full commit SHA

## Repository structure

```text
github-ci-quality-gate/
├── .github/
│   ├── workflows/ci.yml            # the quality gate (4 jobs)
│   ├── workflows/codeql.yml        # static analysis (Security tab)
│   ├── ISSUE_TEMPLATE/             # bug report + feature request forms
│   └── pull_request_template.md
├── src/quality_gate_demo/          # the exercised code (validators)
├── tests/                          # pytest suite (unit + edge cases)
├── docs/                           # architecture, security,
│                                   # troubleshooting, legal applicability
├── scripts/
│   ├── local_ci.sh                 # full local mirror of CI
│   └── validate_workflows.py       # workflow policy validator
├── pyproject.toml                  # pytest, coverage, ruff, bandit config
├── requirements-dev.txt            # exact pinned tool versions
├── .pre-commit-config.yaml         # convenience hooks (CI stays authoritative)
├── CONTRIBUTING.md / SECURITY.md / CHANGELOG.md / LICENSE
└── README.md
```

## Prerequisites

- Python **3.12 or newer** (`python --version`)
- `pip` (bundled with Python)
- Git, and optionally `uv` (the setup script uses it if available)

## Local setup

```bash
git clone https://github.com/fabiljayson/github-ci-quality-gate.git
cd github-ci-quality-gate

python3 -m venv .venv
source .venv/bin/activate                    # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

`requirements-dev.txt` pins the exact versions CI installs, so your local
environment and CI run the same tools.

### Run the full gate locally

```bash
./scripts/local_ci.sh
```

(The script reuses `.venv`, creating it with `uv` if you have `uv`.)

### Run each check individually

```bash
python -m pytest --cov --cov-report=term-missing --cov-fail-under=90   # tests
ruff check .                                                          # lint
ruff format --check .                                                 # format
bandit -r src -c pyproject.toml --quiet                               # source scan
pip-audit --strict                                                    # dependency audit
python scripts/validate_workflows.py                                  # workflow policy
```

### Windows (PowerShell) equivalents

```powershell
python -m venv .venv; .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest --cov --cov-fail-under=90
ruff check .
ruff format --check .
bandit -r src -c pyproject.toml --quiet
pip-audit --strict
python scripts\validate_workflows.py
```

Optional convenience: `pre-commit install` hooks (Ruff autofix, YAML and
whitespace hygiene). CI remains the authoritative gate.

## How CI decides your PR

```text
on: pull_request → main | push → main | workflow_dispatch

┌ Tests (Python 3.12 / 3.13 / 3.14) ── install pinned deps ── pytest
│                                    coverage ≥ 90 %, junit/xml artifacts
├ Code quality (Ruff)                ── lint + format verification
├ Security (Bandit + pip-audit)      ── bandit src scan, pip-audit --strict
└ Workflow validation               ── policies over the workflows themselves
                 all four jobs in parallel, each with its own timeout
```

Everything is read-only (`permissions: contents: read`), no secrets are
used, and fork pull requests run under the same restricted context.

### Example outcomes

**Passing PR** (all checks complete):

```text
Tests (Python 3.14)           ✔ 5:07   78 passed
Code quality (Ruff)           ✔ 0:14   0 findings
Security (Bandit + pip-audit) ✔ 0:31   0 known CVEs
Workflow validation           ✔ 0:12   2 files OK
```

**Failing PR** (examples of each job's feedback):

```text
Tests        FAILED  FAILED tests/test_validator.py::TestPort::test_rejects[65536]
                     Required coverage of 90% reached: 100.00%   (or not!)
Code quality FAILED  ruff: F401 unused import · would reformat 1 file
Security     FAILED  bandit: [B105] hardcoded password string ·
                     pip-audit: Found 1 known vulnerability (pipeline broken)
Workflow val FAILED  job 'tests' action 'actions/checkout@v5' is not pinned
                     to a full 40-character commit SHA
```

Each failed step logs the reason; artifacts
(`test-reports-py*`, `bandit-report`) stay downloadable for 5 days.

## Branch protection setup

> **Status in this repository: already enabled.** A branch ruleset named
> `protect-main` (ruleset id `25788221`) enforces: pull requests only, the
> six status checks below required and green, branches up to date before
> merging, no bypass for administrators. The steps are kept so this gate
> can be reproduced on any other repository.

To turn the gate from advisory into **enforced**, a repository
administrator configures rules that require the CI jobs to pass before a
merge is possible.

> A green workflow alone never blocks anything. Enforcement always lives
> in repository settings, some of which depend on your plan.

1. Open **Settings → Rules → Rules sets → New branch ruleset** (or the
   classic *Settings → Branches → Add branch protection rule*).
2. Name it (e.g. `protect-main`), set **Enforcement status: Active**, and
   target the branch `main` (`Add a target:` `Bypass list` empty).
3. Enable **Require a pull request before merging** (classic interface)
   or *Require contributions from contributors before merging* (rulesets).
4. Enable **Require status checks to pass before merging**, then search
   and select **These exact check names from this repo**:

   - `Tests (Python 3.12)`
   - `Tests (Python 3.13)`
   - `Tests (Python 3.14)`
   - `Code quality (Ruff)`
   - `Security (Bandit + pip-audit)`
   - `Workflow validation`

5. Optionally enable **Require branches to be up to date before merging**
   (prevents "passes on base, breaks when merged"), approval counts, and
   **Do not allow bypassing the above settings** (sometimes shown as
   *Apply rulesets to admins*).
6. Verify: open a PR with a deliberate test or lint failure → the merge
   button stays blocked; fix it → the PR becomes mergeable.

Signatures of the same four job names live in `docs/troubleshooting.md`.

## Troubleshooting

See `docs/troubleshooting.md` for a symptom-first guide: pending checks,
red jobs per tool (pytest/Ruff/Bandit/pip-audit), and *exact* required
check-name strings to paste into branch protection.

## Security limitations

Documented fully in `docs/security.md`; the honest summary:

- Bandit scans Python source only (`src/`), not scripts.
- pip-audit covers **installed** environments, not future CVEs or
  unvetted zero-days.
- SHA pinning protects against tag rewrites, not malicious upstream code
  at the pinned commit.
- CodeQL adds static reach but no dynamic coverage and no other languages.
- Enforcement of the gate depends on branch protection being configured
  by a repository administrator (not enforced by the workflows alone).

## Known limitations

- Windows has no scripted one-command mirror (per-command PowerShell
  equivalents are documented above).
- The demo package is intentionally minimal — extending it is the
  exercise, not the objective.
- Coverage threshold (90 %) and Python version matrix are choices, not
  laws; review them when the code changes.

## Contributing

See `CONTRIBUTING.md` for branch naming, PR conventions, testing
expectations, and the dependency-update recipe. Security issues go
through `SECURITY.md` (private reporting).

## License

[MIT](./LICENSE) — free to use, fork, and adapt, with no warranty.

Documentation for it is in `docs/legal-applicability.md` (why a Privacy
Policy / ToS is **not** required for this data-free, service-free repo).

## Project completion status

| Requirement | Status |
|---|---|
| CI triggers: PR + push + manual | ✅ |
| Tests with pytest + coverage gate | ✅ (78 tests, 100 % cover) |
| Ruff lint + format verification | ✅ |
| Bandit + pip-audit + CodeQL | ✅ |
| Workflow self-validation | ✅ |
| Least privilege / no secrets in fork PRs | ✅ |
| SHA-pinned actions | ✅ |
| Local mirror (`local_ci.sh`) | ✅ |
| Branch protection enforced | ✅ ruleset `protect-main` (id 25788221) active |
| Docs set (README/arch/security/troubleshooting) | ✅ |
| Legal applicability assessed | ✅ (no extra policy needed; documented) |
