# Security Policy

## Supported versions

The project follows a rolling-main model: security fixes are applied to
the latest commit on the `main` branch only. Tagged releases are
snapshots; if you use one, prefer pulling `main` or the newest tag.

| Version | Branch | Supported |
|---------|--------|-----------|
| latest (`main`) | `main` | Yes |
| older tags | — | No |

## Reporting a vulnerability

Do **not** open a public GitHub issue for a suspected security problem.

Use GitHub's private vulnerability reporting (repository **Security** tab →
*Report a vulnerability*), which notifies the maintainers privately. The
repository has no dedicated security email; if private reporting is
unavailable for some reason, contact the owner `fabiljayson` directly
through a private channel you already have, instead of disclosing publicly.

## What to include in a report

- The affected workflow, script, or validator module.
- Steps to reproduce or a proof of concept.
- The impact you consider realistic (be conservative).

## Response process

1. Acknowledge the report within **5 business days**.
2. Assess and prepare a fix on a private topic branch.
3. Publish the fix, mention it in the CHANGELOG, and only then allow the
   report to be closed/disclosed publicly (coordinated disclosure).

## Disclosure expectations

Please do not publicly disclose exploitable vulnerabilities before the
coordinated fix is released. This is a small educational pipeline; reports
will still be handled seriously.

## Scope notes

- The CI pipeline is **read-only** by design: fallback PRs from forks run
  with `contents: read` and no secrets. Reports about how a fork PR could
  gain privileged access are in scope.
- Dependency vulnerabilities found by pip-audit are handled by bumping
  the pinned version in `requirements-dev.txt`; do not silence findings.
