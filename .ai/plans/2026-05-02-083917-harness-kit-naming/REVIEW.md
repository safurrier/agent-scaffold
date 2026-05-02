---
id: plan-review
title: Harness Kit Naming Review Log
description: >
  External-enough review record for the naming implementation slice.
---

# Review — harness-kit-naming

## Review Context

- Mode: external
- Backend: local-self-review
- Reviewer: primary agent

## Rubrics

- core-quality

## Findings

- Codex multi-agent review found one high-priority issue before merge: apps module names could be treated as raw path components and escape the generated project root.
- Addressed the Codex review findings by validating module names, handling missing `--target` paths without tracebacks, tightening portable validation command detection, requiring external review notes for portable sync-check, making the Go format check non-mutating, fixing exact slug duplicate detection, adding the `HARNESS_KIT_WORKFLOW_HOME` variable, fixing stale docs references, and replacing a type ignore with `cast`.
- The rename intentionally has no backwards-compatible console scripts: `agent-scaffold` and `agent-workflow` are not declared in `pyproject.toml`.
- The Python import package is now `harness_toolkit`; no `agent_scaffold` shim is kept.
- Public commands now separate the product surfaces:
  - `harness-scaffold` for starter-template init
  - `hk` / `harness-kit` for portable workflow operations
- Historical ADR identifiers may still contain `agent-scaffold`; ADR 0007 documents those as historical names.

## Disposition

- CI passed after marking both changed plans complete.
- Codex review findings addressed; ready for final validation and human review.
