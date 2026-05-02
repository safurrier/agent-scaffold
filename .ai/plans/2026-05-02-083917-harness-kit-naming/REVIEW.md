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

- The rename intentionally has no backwards-compatible console scripts: `agent-scaffold` and `agent-workflow` are not declared in `pyproject.toml`.
- The Python import package is now `harness_toolkit`; no `agent_scaffold` shim is kept.
- Public commands now separate the product surfaces:
  - `harness-scaffold` for starter-template init
  - `hk` / `harness-kit` for portable workflow operations
- Historical ADR identifiers may still contain `agent-scaffold`; ADR 0007 documents those as historical names.

## Disposition

- Ready for full validation after final formatting.
