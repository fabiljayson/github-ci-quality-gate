#!/usr/bin/env python3
"""Local structural validation of the repository GitHub workflows.

This complements GitHub's own schema validation, which happens server-side
when a workflow is loaded. It checks invariants that keep the pipeline safe:
every job has a timeout, the workflow declares permissions, actions are
pinned by full commit SHA, and fork-unsafe events are not used.

Exit codes: 0 = all checks passed, 1 = at least one failure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

WORKFLOWS_DIR = Path(".github/workflows")
FORK_UNSAFE_EVENTS = {"pull_request_target", "repository_dispatch"}
SHA_PATTERN = re.compile(r"@[0-9a-f]{40}(?:\s|$)")


def check_workflow(path: Path) -> list[str]:
    """Validate one workflow file and return a list of error strings."""
    errors: list[str] = []
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"{path}: invalid YAML ({exc})"]

    if not isinstance(document, dict):
        return [f"{path}: workflow must map to a key/value document"]
    if not document.get("name"):
        errors.append(f"{path}: missing 'name'")
    if "permissions" not in document:
        errors.append(f"{path}: missing workflow-level 'permissions' block")
    if "jobs" not in document:
        errors.append(f"{path}: missing 'jobs' block")

    # PyYAML reads the unquoted `on:` key of a workflow as the boolean True.
    triggers = document.get("on") or document.get(True) or {}
    unsafe = set(triggers) & FORK_UNSAFE_EVENTS
    if unsafe:
        errors.append(
            f"{path}: uses fork-unsafe trigger(s) {sorted(unsafe)}; "
            "ordinary CI must not run fork code with escalated privileges"
        )

    for job_name, job in (document.get("jobs") or {}).items():
        if not job.get("timeout-minutes"):
            errors.append(f"{path}: job '{job_name}' missing 'timeout-minutes'")
        for step in job.get("steps", []):
            uses = step.get("uses", "")
            if not uses:
                continue
            if uses.startswith(("./", "docker://")):
                continue  # local reusable workflow or container image
            if not SHA_PATTERN.search(uses):
                errors.append(
                    f"{path}: job '{job_name}' action '{uses}' is not "
                    "pinned to a full 40-character commit SHA"
                )
    return errors


def main() -> int:
    paths = sorted(WORKFLOWS_DIR.glob("*.yml")) + sorted(WORKFLOWS_DIR.glob("*.yaml"))
    if not paths:
        print(f"FAIL: no workflow files found in {WORKFLOWS_DIR}/")
        return 1

    all_errors: list[str] = []
    for path in paths:
        errors = check_workflow(path)
        print(("FAIL " if errors else "PASS ") + str(path))
        all_errors.extend(errors)

    if all_errors:
        print()
        for error in all_errors:
            print(f"- {error}")
        return 1
    print(f"\nOK: {len(paths)} workflow file(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
