# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org).

## [0.1.0] - 2026-10-24

### Added

- Sample validation package `quality_gate_demo` (project name, TCP port,
  email, password rules) with a stable `ValidationError` contract.
- 78 pytest tests: parametrized unit tests, boundary cases, type handling,
  regression guards; 100 % line and branch coverage enforced in CI.
- GitHub Actions quality gate (`ci.yml`) with four parallel jobs:
  - **Tests** — pytest on Python 3.12 / 3.13 / 3.14 with coverage
    reporting and uploaded test/coverage artifacts.
  - **Code quality** — Ruff lint and format verification.
  - **Security** — Bandit source scan and pip-audit dependency audit.
  - **Workflow validation** — local structural checks of the workflow files
    themselves (`scripts/validate_workflows.py`).
- CodeQL static analysis as a separate workflow (`codeql.yml`).
- Local mirror of all CI checks: `scripts/local_ci.sh` (Linux/macOS) plus
  documented Windows PowerShell equivalents.
- Pre-commit hooks (Ruff lint + format, YAML, whitespace hygiene).
- Full documentation set: README, CONTRIBUTING, SECURITY, and
  `docs/architecture.md`, `docs/security.md`, `docs/troubleshooting.md`,
  `docs/legal-applicability.md`.
