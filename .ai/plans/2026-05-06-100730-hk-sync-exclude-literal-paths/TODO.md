---
id: plan-todo
title: Task List
description: >
  Checkable tasks for this unit of work. Check off as you go.
  See _example/ for a reference.
---

# TODO — hk-sync-exclude-literal-paths

- [x] Document the user correction in `AGENTS.md`.
- [x] Remove the hardcoded `.pi` / `.claude/worktrees` allowlist from `hk sync --exclude` enforcement.
- [x] Keep literal path normalization and root/absolute/`..`/pathspec rejection.
- [x] Keep untracked-only safety by rejecting tracked/staged paths and tracked descendants.
- [x] Preserve stored exclusion metadata and revalidation during sync checks/readiness.
- [x] Update tests for arbitrary untracked literal exclusions and staged/tracked rejection.
- [x] Update README/SPEC/design/portable docs.
- [x] Run focused quality gates.
- [x] Run fresh-context review.
- [x] Run HK dogfood and save evidence/handoff artifacts.
