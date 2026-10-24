# Contributing

Thanks for helping improve this quality-gate demo. The project is small on
purpose; keep changes focused and let the gate do the reviewing.

## Getting started

```bash
git clone https://github.com/fabiljayson/github-ci-quality-gate.git
cd github-ci-quality-gate
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

(Windows PowerShell: `python -m venv .venv; .venv\Scripts\Activate.ps1`.)

## Branch and commit conventions

- Branch from `main`, name it after the topic:
  `fix/<topic>`, `feat/<topic>`, `docs/<topic>`.
- One logical change per pull request.
- Commit messages in the imperative mood
  ("Add timeout to security job").

## Pull-request process

1. Open the PR against `main` and fill the PR template.
2. The CI quality gate runs automatically; all four jobs must be green.
3. At least one review approval is recommended, but repository rules are
   the real enforcement (see README section "Branch protection").
4. The reviewer may ask you to run extra checks locally.

## Local quality checks

Run everything CI runs, before pushing:

```bash
./scripts/local_ci.sh          # Linux/macOS — runs the full suite
```

Or individually (identical to the CI jobs):

```bash
python -m pytest --cov --cov-fail-under=90   # tests + coverage
ruff check .                                 # lint
ruff format --check .                        # formatting verification
bandit -r src -c pyproject.toml --quiet      # security scan
pip-audit --strict                           # dependency audit
python scripts/validate_workflows.py         # workflow configuration
```

## Testing expectations

- New behaviour in `src/quality_gate_demo/` must come with tests.
- Bug fixes need at least one regression test that failed before the fix.
- Keep tests deterministic: no network, no credentials, no sleeps.

## Security and dependency updates

- To update six dependencies, run
  `python -m pip install -U <tool> && python -m pip freeze > requirements-dev.txt`
  and let pip-audit confirm the new versions are clean.
- Never commit secrets, tokens, or machine-specific paths.
- If you find a vulnerability, follow `SECURITY.md` (private reporting).
