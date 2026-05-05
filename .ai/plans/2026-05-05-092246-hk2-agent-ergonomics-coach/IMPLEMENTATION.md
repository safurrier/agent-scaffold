---
id: plan-implementation
title: Implementation Plan
description: >
  Step-by-step approach for this unit of work.
  Optional — create only when the approach isn't obvious.
---

# Implementation — hk2-agent-ergonomics-coach

## Approach

Implement the ergonomic fixes as a lifecycle CLI polish slice, not a new workflow substrate. Start with CLI semantics and ledger events, then improve rendering/guidance, then update docs/tests, then dogfood the resulting happy path in temporary repositories.

## Steps

1. Inspect current HK2 lifecycle implementation in `src/harness_toolkit/kit/cli.py`, `workflow.py`, and `local.py`.
2. Add `--plan` and `--context` options to `hk start`.
   - Starting work still creates the same work record.
   - `--plan` appends a lifecycle plan event immediately.
   - `--context` appends a context event immediately when provided.
3. Clarify slug guidance in help/docs.
   - Slug is a short human-readable task name.
   - Chronological ordering comes from HK-generated timestamps/work IDs.
4. Make root `hk plan` lifecycle-only.
   - Remove any legacy plan-creation fallback from root `hk plan`.
   - Confirm `hk legacy plan <slug>` remains the only old artifact-creation path.
5. Upgrade `hk status`.
   - Show active work slug/target.
   - Show missing plan before implementation.
   - Show optional context guidance without making context mandatory.
   - Show missing decision/spec-impact reflection once changes exist.
   - Show validation, independent review, sync, and agent-local state guidance.
6. Add `hk dangerously-skip sync --reason '...'`.
   - Require `--reason`.
   - Record the skip as a dangerous skip event.
   - Treat sync readiness as satisfied by the dangerous skip.
   - Render the skip prominently in handoff.
7. Update help examples, README, SPEC, design docs, and profile/dogfood guidance.
8. Add unit/e2e tests for:
   - `start --plan` records a plan event;
   - `start --context` records a context event;
   - root `hk plan` no longer creates legacy artifacts;
   - `status` next-action output;
   - `dangerously-skip sync` readiness/handoff behavior;
   - legacy plan path still works under `hk legacy plan`.
9. Run focused tests, then `mise run check`.
10. Run a targeted PR-sized dogfood rerun in temporary repos with three workers focused on `start --plan`, `status`, and sync skip behavior.
11. Capture rollout findings as a plan artifact and complete review/sync-check.
