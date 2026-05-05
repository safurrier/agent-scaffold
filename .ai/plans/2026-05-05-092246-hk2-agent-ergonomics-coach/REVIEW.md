---
id: plan-review
title: Review Log
description: >
  External-enough review record for this slice. Capture the backend, rubrics,
  findings, and final disposition before handoff.
---

# Review — hk2-agent-ergonomics-coach

## Review Context

- Mode: external
- Backend: pi subagent
- Reviewer: fresh-context reviewer

## Rubrics

- core-quality
- cli-ergonomics
- dogfood-evidence

## Findings

- Initial review found blockers in sync-skip semantics and dogfood artifact handling; both were fixed.
- Re-review confirmed the sync-skip fix and found handoff-contract cleanup issues; those were fixed before final sync-check.

### Initial review

Reviewer found two blockers and several notes:

- Blocker: `dangerously-skip sync` could satisfy readiness without a prior `hk sync` checkpoint.
- Blocker: dogfood artifacts were listed in the manifest but not visible to reviewer in a commit-ready form.
- Note: `hk instructions` still promoted separate `hk start` + `hk plan` instead of `hk start --plan`.
- Note: profile-authoring references still used root `hk sync-check` examples.

### Fixes

- Required a prior `sync_checkpoint` before recording a dangerous sync skip.
- Made `sync --check` and `sync_status_for()` consider sync skips only when a prior checkpoint exists.
- Added regression tests for sync skip requiring a prior checkpoint and going stale after later lifecycle work.
- Promoted `hk start --plan` in generated instructions snippets and tests.
- Updated profile-authoring references to use `hk legacy sync-check` for legacy plan artifacts.
- Copied dogfood evidence as top-level reviewable plan artifacts and updated the manifest.
- Fixed `META.yaml` `decision_record` to use the allowed `adr` value.

### Re-review

Reviewer confirmed the sync-skip blocker, instructions note, and manifest existence were addressed, then identified remaining handoff issues:

- `META.yaml` had an invalid `decision_record` value.
- Nested `artifacts/dogfood-v3/` files were ignored by git and therefore not commit-ready.
- Additional profile-authoring examples still used root `hk sync-check`.

Those issues were fixed as above. Final sync-check is pending.

## Disposition

- Accepted after review fixes; final sync-check passed.
