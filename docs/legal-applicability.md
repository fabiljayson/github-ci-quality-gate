# Legal applicability assessment

This repository is a **public educational CI project**. It ships only:
source code, tests, and GitHub Actions configuration. It does not run any
service of its own, does not process personal data beyond what the GitHub
platform inevitably handles, and has no end users of a hosted product.
The following records why full application-legal documents are (for now)
not required — and what to add if that ever changes.

> This file is a scope decision, **not legal advice**. Re-assess whenever
> the project's behaviour changes.

## 1. Privacy Policy — not required at this stage

**Decision:** no standalone Privacy Policy document.

**Reasoning:**

- The project executes only within the contributor's machine and on
  GitHub runners. It collects, stores, and transmits **no personal data**.
  Test runs use synthetic values (`alice@example.org`,
  `S3cure!Passw0rd`…); no telemetry, accounts, or cookies exist.
- Account data, repository metadata, and workflow logs are processed by
  **GitHub, Inc.** under its own [Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement),
  not by this project.

**Trigger to re-open this assessment:** adding a hosted dashboard,
telemetry/analytics, user accounts, or a service that ingests
third-party data. At that point, draft a real Privacy Policy **and have
it reviewed by legal counsel** before launch.

## 2. Confidentiality policy — covered by existing documents

**Decision:** no standalone document; expectations are distributed:

- Credentials & secrets — `docs/security.md` ("Secrets discipline"):
  never commit secrets; no token exists in any tracked file at the time
  of writing.
- Vulnerability reporting — `SECURITY.md`: private reporting, coordinated
  disclosure, no public disclosure before a fix ships.
- Confidential artifacts — GitHub Actions artifacts in this repo hold
  test/coverage/bandit outputs only, expire after 5 days, and contain no
  private data; sharing workflow logs of public runs is not restricted.

If the repository ever becomes the base of a private/enterprise project,
promote these points into a formal confidentiality policy.

## 3. Terms of Service — not required at this stage

**Decision:** no ToS document.

**Reasoning:** there is no service, no SLA, no hosted compute, no
tiering — nothing to which "terms of use of a service" could apply. The
code is offered under the **MIT License** (see `LICENSE`), which already
defines usage/warranty terms for the code as a product.

**Trigger to re-open:** the first time the project starts offering a
hosted capability to other people (API, dashboard, bot).

## Summary table

| Document | Required? | Where the concern lives instead |
|---|---|---|
| Privacy Policy | No (educational, data-free) | GitHub's own privacy terms; reassess on feature change |
| Confidentiality policy | No (standalone) | `SECURITY.md` + `docs/security.md` |
| Terms of Service | No (no hosted service) | MIT `LICENSE` |

Any future policy would be drafted for **legal review**, not generated
as pretend-legal filler.
