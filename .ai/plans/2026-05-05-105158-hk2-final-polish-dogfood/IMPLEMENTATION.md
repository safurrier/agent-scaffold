---
id: plan-implementation
title: Implementation Plan
description: >
  Step-by-step approach for this unit of work.
  Optional — create only when the approach isn't obvious.
---

# Implementation — hk2-final-polish-dogfood

## Approach

Treat this as a final lifecycle polish slice. Implement explicit constrained sync exclusions first because they affect readiness semantics, then add structured spec impact and review prompt ergonomics, then update status/docs/help, then run less-guided dogfood.

## Steps

1. Inspect current sync hashing/checkpoint code in `src/harness_toolkit/kit/local.py`.
2. Add a non-excluded diff/status hash path.
   - It should behave like current `git_diff_hash()` but omit explicitly excluded pathspecs.
   - It must still include untracked content for non-excluded paths.
3. Extend `sync_checkpoint()` to accept `exclude` paths and `reason`.
   - Reject `--exclude` without `--reason`.
   - Reject excluded paths absent from `git status --porcelain -- PATH`.
   - Store excluded paths/reason and excluded-path metadata on the checkpoint event.
4. Update `sync_status_for()` and `sync --check` to compare non-excluded hashes when the latest checkpoint has exclusions.
5. Render `## Sync exclusions` in handoff when the latest relevant checkpoint used exclusions.
6. Add/adjust tests for:
   - excluded `.pi` path makes readiness pass;
   - source changes after excluded sync make readiness fail;
   - missing reason fails;
   - absent excluded path fails;
   - handoff renders `## Sync exclusions`.
7. Add structured `hk decide` spec impact modes and repeated `--spec-ref`.
   - Preserve `--no-spec-impact` as a compatibility alias for `--spec-impact none`.
   - Store spec impact in a parseable note/event form while keeping handoff readable.
8. Add `hk review prompt`.
   - Include active work, plan, decisions/spec reflection, validation summaries, and changed files.
   - Output a prompt suitable for a fresh-context subagent or external reviewer.
   - Keep policy text: external preferred, fresh-context subagent minimum, implementation-agent self-review invalid.
9. Add status phase labels.
10. Update docs/help/profile references to demote advanced surfaces and document future configurable review sources.
11. Run focused tests and `mise run check`.
12. Run less-guided three-worker PR-sized dogfood in temporary repos:
    - prompt workers only to use HK and begin by exploring CLI;
    - do not name the new features;
    - record whether they naturally discover `sync --exclude`, structured spec impact, review prompt, and status phase guidance.
13. Capture dogfood study and independent review, then run plan sync-check.
