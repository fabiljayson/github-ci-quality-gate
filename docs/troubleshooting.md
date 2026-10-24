# Troubleshooting

Symptom-first guide for the quality gate. Each entry pairs the failure
with its usual cause and the shortest fix.

## CI stays "pending" / merge button stays disabled

- **Cause:** repository rules require status checks and at least one has
  not completed yet, or one of the required checks never ran (e.g. it
  was renamed without updating the rules).
- **Fix:** open the PR's *Checks* tab and identify which of
  `Tests (Python 3.12/3.13/3.14)`, `Code quality (Ruff)`,
  `Security (Bandit + pip-audit)`, `Workflow validation` is missing:
  - still running → wait;
  - failed → see the matching section below;
  - missing → the rule references a stale name — update the required
    check names in *Settings → Rules → Rules set*.

## A merge was allowed despite a red job

- **Cause:** required checks are not configured in repository rules.
  A green workflow alone is only a signal — enforcement lives in
  *Settings → Rules → Rules sets*.
- **Fix:** follow the README section *"Branch protection setup"* and
  mark the four job names as required.

## "Tests" fails

- **Red step:** *Run tests with coverage* — read the failed summary.

```text
FAILED tests/test_validator.py::TestValidatePort::test_rejects_with_expected_code[65536]
```

- **What to fix:** run the same suite locally (`python -m pytest -x`)
  with the CI flags from the log line.
- **Coverage short-fall:** the log shows the line *"Total coverage … below
  the 90 % threshold"* with a missing-lines table. Add or extend tests —
  never lower the threshold casually.
- **Diagnosis:** open the *test-reports-py* artifact for the JUnit file
  and coverage table; reports contain no secrets.

## "Code quality (Ruff)" fails

- **Lint violation (ruff check):**

```text
F401    tests/test_port.py:3: imported but unused
```

  Fix: remove the import, or use real project code if it was taken
  from elsewhere (see `CONTRIBUTING.md`).
- **Format violation (`ruff format --check`):**

```text
would reformat src/quality_gate_demo/validator.py
```

  CI is intentionally read-only: it verifies formatting instead of
  silently rewriting the PR. Run the formatter **locally**, commit, push.
- **Local one-liner:** `ruff check . --fix && ruff format .`,
  then re-run `./scripts/local_ci.sh`.

## "Security (Bandit + pip-audit)" fails

- **Bandit finding:** step *Scan source with Bandit* prints the issue id
  and file. Re-run locally in JSON mode for the full details:

```bash
bandit -r src -c pyproject.toml --quiet -f json -o bandit.json
pip-audit --strict
```

  Fix real findings in the code. Suppress a finding only with a scoped
  `# nosec` marker plus a written justification and a review date —
  broad exclusions to force a green build are forbidden
  (see `docs/security.md`).

- **pip-audit failure mode matters:** a *resolve/download* failure seen
  here was a flake — rerun the job once before diagnosing; pip-audit in
  `--strict` mode deliberately fails on network/resolve problems rather
  than pass silently.

## "Workflow validation" fails

The step output enumerates each violation, e.g.:

```text
- .github/workflows/ci.yml: job 'tests' action 'actions/checkout@v7' is
  not pinned to a full 40-character commit SHA
```

Read the full checklist enforced there (timeout on every job, workflow
permissions declared, fork-unsafe events banned, SHA-pinned actions)
as shown in `docs/security.md`. The same script runs locally:
`python scripts/validate_workflows.py`.

## CI is green but a compliant run looks wrong

- Rerun the workflow once via *Actions → CI → Run workflow* before
  investigating deeper; runner flakes (network, image drift) are rare
  but non-zero.

## pip-audit runs "somewhere local" but not in CI (and vice versa)

- CI scans the environment installed from `requirements-dev.txt`; your
  local box may have extra (or older) tools installed in the venv.
  Recreate the venv to compare one-to-one: see README, *"Local setup"*.

## Status checks on the PR — exact names

Let GitHub type-check the required check names against this table:

| Exact status check name | Job |
|---|---|
| `Tests (Python 3.12)` | matrix cell 3.12 |
| `Tests (Python 3.13)` | matrix cell 3.13 |
| `Tests (Python 3.14)` | matrix cell 3.14 |
| `Code quality (Ruff)` | ruff check + format verify |
| `Security (Bandit + pip-audit)` | bandit + pip-audit |
| `Workflow validation` | scripts/validate_workflows.py |
