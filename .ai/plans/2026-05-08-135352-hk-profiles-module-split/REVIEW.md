---
id: plan-review
title: Review Log
description: >
  External-enough review record for this slice. Capture the backend, rubrics,
  findings, and final disposition before handoff.
---

# Review — hk-profiles-module-split

## Review Context

- Mode: external
- Backend: Pi subagent tool
- Reviewer: fresh-context `reviewer` subagent

## Rubrics

- core-quality
- behavior preservation
- import compatibility
- module locality

## Findings

Initial blockers:

- Root package re-export compatibility missed `BUILTIN_PROFILES` and `loaded_builtins`.
- `profiles_to_json({})` no longer preserved the previous falsy-empty-catalog fallback behavior.

Fixes:

- Restored the re-exports.
- Restored `profiles_to_json({})` fallback.
- Added tests in `tests/unit/test_profile_package_boundaries.py`.

Details: `artifacts/review-summary.md`.

## Disposition

- Accepted after fixes.
- Re-review found no blockers.
