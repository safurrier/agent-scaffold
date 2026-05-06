---
id: plan-implementation
title: Implementation Notes
description: >
  Design and implementation notes for the slice.
---

# IMPLEMENTATION — hk-sync-exclude-literal-paths

## Code changes

- Renamed the previous allowlist constant to `COMMON_AGENT_LOCAL_STATE_PATHS` and kept it only for status guidance that suggests common agent-local paths currently present in git status.
- Removed `is_allowed_sync_exclude_path()` from the enforcement path.
- Changed `sync_exclude_safety_error()` so the safety gate is now:
  1. `git ls-files -- PATH` must report no tracked descendants;
  2. `git status --porcelain -- PATH` must be non-empty;
  3. every porcelain line for the path must be untracked (`??`).
- Kept `normalize_exclude_paths()` protections for empty/root, absolute, `..`, and pathspec/glob-like inputs.
- Left `excluded_path_metadata()` and `sync_checkpoint(check=True)` revalidation intact.

## Test changes

- Replaced the `.pi`-specific happy path with a generic `tmp-output/` untracked literal-path happy path.
- Added coverage that an arbitrary untracked literal file (`src/scratch.py`) is allowed.
- Added/kept rejection coverage for root, absolute, `..`, pathspec/glob, tracked paths, staged paths, and directories with tracked descendants.
- Kept regression coverage that non-excluded source changes after a checkpoint make sync stale.

## Docs

Updated README, SPEC, portable workflow, design docs, and repo agent guidance to state that exclusions are not limited to `.pi`/`.claude`, while preserving the untracked-only recorded/revalidated safety envelope.
