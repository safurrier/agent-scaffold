---
id: plan-todo
title: Task List
description: >
  Checkable tasks for this unit of work. Check off as you go.
---

# TODO — hk2-dogfood-ux-fixes

## Planning

- [x] Create slice plan for dogfood-driven HK 2.0 UX fixes.
- [x] Draft scope and acceptance criteria.
- [x] Ask user follow-up questions on UX policy tradeoffs.
- [x] Update this plan based on questionnaire answers.

## Persist dogfood workflow

- [x] Add repo-local skill `.agent/skills/hk-pr-sized-dogfood/SKILL.md`.
- [x] Include minimal-prompt worker protocol, temp snapshot setup, HK command logging, worker reports, parent readiness/handoff capture, and synthesis checklist.
- [x] Cross-link the skill from repo-local agent docs where appropriate.

## CLI/dev invocation and target story

- [x] Add a current-HK dev shim/task that avoids `uv --directory` target confusion.
- [x] Document when to use the shim versus installed `hk`.
- [x] Add tests/docs for target behavior if implementation changes.

## Command discoverability fixes

- [x] Make bare `hk evidence` fail with a direct hint to `hk evidence list`.
- [x] Move/hide lifecycle-confusing legacy commands under `hk legacy` or remove them from root help.
- [x] Improve `hk start`/root/ready guidance for the minimum readiness loop.
- [x] Make `hk context` visible as optional but useful for PR-sized constraints/repo facts.

## Readiness/handoff wording

- [x] Render failed validation evidence as attempted validation, not successful validation.
- [x] Ensure readiness failure copy stays actionable for missing plan/decision/review/sync.

## Sync freshness policy

- [x] Add warning/diagnostic copy for common agent-local state such as `.pi/` when it affects sync freshness.
- [x] Capture follow-up design notes for an explicit ignore/override mechanism (`.harnessignore`, harness ignore config, or scary sync override) without silently ignoring paths in this slice.

## Dogfood rerun

- [x] Rerun PR-sized dogfood with varied tasks after fixes.
- [x] Capture rerun findings in `artifacts/pr-sized-dogfood-rerun.md`.

## Validation/review

- [x] Add/update unit tests for behavior changes.
- [x] Run focused tests.
- [x] Run `mise run check`.
- [x] Run fresh-context review.
- [x] Run `mise run sync-check`.
