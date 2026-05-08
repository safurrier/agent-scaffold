---
id: plan-spec
title: Slice Spec
description: >
  Behavioral envelope for this change.
---

# SPEC — hk-sync-exclude-literal-paths

## Goal

`hk sync --exclude PATH --reason TEXT` should allow explicit, literal, untracked local-only paths without requiring them to live under a tiny hardcoded allowlist such as `.pi` or `.claude/worktrees`.

## Requirements

- Exclusions remain explicit and auditable: every excluded path requires a reason and is recorded in the sync checkpoint.
- Stored checkpoint exclusions continue to include path metadata and are revalidated during `hk sync --check`, `hk status`, and readiness evaluation.
- HK must reject unsafe exclusion shapes:
  - repository root;
  - absolute paths;
  - paths containing `..`;
  - git pathspec/glob inputs.
- HK must reject paths that are not local-only untracked state:
  - missing paths;
  - tracked paths;
  - staged paths;
  - directories with tracked descendants.
- Excluding one local path must not hide later non-excluded tracked/source changes.

## Non-goals

- No persistent ignore configuration in repo files.
- No broad sync skip replacement; `dangerously-skip sync` remains the explicit fallback for exceptional cases.
