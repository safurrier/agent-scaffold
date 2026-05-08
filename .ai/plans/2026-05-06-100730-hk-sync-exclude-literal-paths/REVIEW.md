---
id: plan-review
title: Review Evidence
description: >
  External review notes for this slice.
---

# REVIEW — hk-sync-exclude-literal-paths

## Review Context

- Mode: external
- Backend: pi-subagent
- Reviewer: reviewer builtin, fresh context

## Rubrics

- core-quality
- sync-exclusion-safety

## Findings

- No blockers.
- Reviewer confirmed the `.pi` / `.claude` hard allowlist was removed from enforcement.
- Reviewer confirmed `sync_exclude_safety_error()` now validates safety properties instead of prefix membership.
- Reviewer confirmed literal path normalization still rejects root, absolute, `..`, and pathspec/glob-like inputs.
- Reviewer confirmed tracked/staged/source safety is preserved through `git ls-files` and porcelain status checks.
- Reviewer confirmed stored checkpoint excludes are revalidated during sync checks/status.
- Reviewer suggested adding explicit absolute-path and staged-new-path coverage, and aligning `docs/harness-kit-lifecycle-design.md`.

## Disposition

- Addressed reviewer suggestions by adding absolute-path rejection coverage.
- Addressed reviewer suggestions by adding staged-new-path rejection coverage.
- Updated `docs/harness-kit-lifecycle-design.md` to match the no-hardcoded-allowlist behavior.
- Filled and synced the plan artifacts before handoff.
