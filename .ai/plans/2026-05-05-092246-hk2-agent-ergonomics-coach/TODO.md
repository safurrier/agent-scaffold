---
id: plan-todo
title: Task List
description: >
  Checkable tasks for this unit of work. Check off as you go.
  See _example/ for a reference.
---

# TODO — hk2-agent-ergonomics-coach

## Design and context

- [x] Gather structured user decisions with questionnaire.
- [x] Capture questionnaire summary artifact.
- [x] Clarify slug guidance and `hk plan` vs `hk start --plan` semantics.

## Implementation

- [x] Add `hk start <slug> --plan '...'`.
- [x] Add optional `hk start <slug> --context '...'`.
- [x] Update start/help output with slug guidance and lifecycle next steps.
- [x] Make root `hk plan` lifecycle-only.
- [x] Keep legacy artifact plan creation under `hk legacy plan <slug>`.
- [x] Upgrade `hk status` into a preflight / next-action coach.
- [x] Add `hk dangerously-skip sync --reason '...'`.
- [x] Ensure dangerous sync skip satisfies readiness and renders in handoff.

## Tests

- [x] Test `start --plan` records a lifecycle plan event.
- [x] Test `start --context` records a context event.
- [x] Test root `hk plan` no longer creates legacy artifacts.
- [x] Test `hk legacy plan` still works for old artifact workflow.
- [x] Test `hk status` coaching output for missing plan/context/decision/validation/review/sync.
- [x] Test `dangerously-skip sync` requires a reason.
- [x] Test dangerous sync skip makes `ready` pass sync freshness and appears in handoff.

## Docs

- [x] Update `README.md` happy path.
- [x] Update `SPEC.md` requirements.
- [x] Update `docs/harness-kit-lifecycle-design.md`.
- [x] Update `docs/portable-workflow.md` if root/legacy examples are affected.
- [x] Update `.agent/skills/hk-pr-sized-dogfood/SKILL.md` for targeted rerun instructions.

## Validation and dogfood

- [x] Run focused unit/e2e tests.
- [x] Run `mise run check`.
- [x] Run targeted three-worker PR-sized dogfood rerun in temp repos.
- [x] Capture dogfood rerun study artifact.
- [x] Get independent/fresh-context review.
- [x] Run `mise run sync-check -- --plan-dir .ai/plans/2026-05-05-092246-hk2-agent-ergonomics-coach`.
