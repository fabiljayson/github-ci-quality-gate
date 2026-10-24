# Security model

## Threat model

Assets to protect: source code integrity on `main`, CI compute, secrets,
and the reference newcomers will copy.

Adversaries considered:

1. **Malicious fork PR** — untrusted code submitted as a pull request.
2. **Weak project code** — bugs introduced by maintainers themselves.
3. **Compromised dependency** — a deliberately malicious package version.
4. **Compromised Actions/tags** — a maintainer tag rewritten upstream.

## Fork pull requests

The repo blocks none of them by design: `ci.yml` uses the `pull_request`
event, which runs forked code within the fork's read-only token context:

- The token has `contents: read` and nothing else; it is isolated per job.
- No secret exists in the repository at the time of writing — and even if
  one were added, secrets are **not** provided to workflows triggered by
  `pull_request` from forks.
- `pull_request_target` is never used for test execution; the workflow
  validator (`scripts/validate_workflows.py`) fails a build if it ever
  appears, so the safeguard is machine-enforced, not just documented.
- No untrusted event data is interpolated into shell commands (`run:`)
  and no `github.event.*` value reaches `env:` or `with:`.

## Token and permission discipline

- Workflow level: `permissions: contents: read` (least privilege).
- Job level: no extra grants anywhere in `ci.yml`.
- The single documented exception is `codeql.yml`, which needs
  `security-events: write` to upload SARIF to the Security tab.

## Action pinning

Every third-party action reference is pinned to a **full commit SHA**
(file history records the SHA → release mapping in an inline comment).
Pinning by SHA defeats tag rewrites (e.g. a compromised v7 tag), at the
cost of manual updates. Update procedure:

1. Look up the new release commit SHA (e.g. `gh api repos/actions/checkout/commits/main --jq .sha`).
2. Replace both the SHA and the version comment in every workflow where
   the action appears.
3. Run `./scripts/local_ci.sh`; the validator fails if a plain tag is
   accidentally reintroduced.

## Scanners and their coverage boundaries

| Tool | Covers | Cannot cover |
|---|---|---|
| pytest (+ coverage gate) | behavioural bugs | intent |
| Ruff | lint/format class defects | runtime behaviour |
| Bandit | common Python weakness patterns (source-level) | logic flaws, dependency CVEs, non-Python files |
| pip-audit | **installed** packages vs known CVEs | zero-day or unvetted packages, npm/docker ecosystems |
| CodeQL | data-flow/static analysis (Python) | dynamic issues, configuration outside repository |
| Script validator | policy invariants (SHA pins, timeouts, fork-unsafe events) | semantic workflow mistakes |

pip-audit audits the environment installed from `requirements-dev.txt`
(the same file CI installs from), not the bare manifest, so the audit is
about **the lock-reality of CI** rather than declared intentions.
Dev-tooling CVEs also surface there; they are triaged the same way.

## Secrets discipline

- No repository secrets are used; nothing to leak.
- If a secret is ever added, add it under Actions/OIDC with the narrowest
  scope, keep it out of `env:` for shell interpolation, and remember fork
  PRs never receive secrets in `pull_request` workflows.
- The validator forbids `pull_request_target`, closing the classic
  "privileged run + fork code" escalation path.

## Known limitations

1. Docker/uv-alarmed npm ecosystems are not covered (the project has
   neither; if this changes, add their scanners).
2. Bandit runs against `src/` only; `scripts/` is developer tooling and
   inspected by Ruff plus CodeQL instead.
3. Outdated-action compromise is mitigated (SHA pinning) but not
   prevented: if **upstream code itself** turns malicious at the pinned
   SHA, only review and incident response remain.
4. Branch protection is configured in repository settings; until the
   apply, the gate advises but does not enforce merges.
