---
id: plan-decisions
title: Decisions
description: >
  Decision log for the slice.
---

# DECISIONS — hk-sync-exclude-literal-paths

## What Changed

- Removed the `.pi` / `.claude/worktrees` enforcement allowlist from `hk sync --exclude`.
- HK now allows any explicit literal untracked local-only path that passes safety checks and records it in the sync checkpoint.
- Preserved checks for root/pathspec/absolute/`..`, missing paths, tracked/staged paths, tracked descendants, and non-excluded source changes.

## Why

- The user clarified that real repos can have many local-only generated files, tool caches, scratch outputs, and agent artifacts that may need to be excluded from a freshness checkpoint.
- Hardcoding only `.pi`/`.claude` would force unnecessary dangerous sync skips or cleanup work.
- The desired safety property is explicit recorded exclusions plus revalidation, not a tiny hardcoded allowlist.

## Where Reflected

- `src/harness_toolkit/kit/local.py`
- `tests/unit/test_harness_kit_2.py`
- `README.md`
- `SPEC.md`
- `docs/portable-workflow.md`
- `docs/harness-kit-lifecycle-design.md`
- `AGENTS.md`

## Promotion

- No ADR needed for this small correction; the behavior is reflected in product docs and regression tests.
