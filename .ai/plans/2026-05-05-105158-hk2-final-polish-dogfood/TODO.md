---
id: plan-todo
title: Task List
description: >
  Checkable tasks for this unit of work. Check off as you go.
  See _example/ for a reference.
---

# TODO — hk2-final-polish-dogfood

## Design and planning

- [x] Gather structured user decisions with questionnaire.
- [x] Capture questionnaire summary artifact.
- [x] Clarify repeated `--exclude` means multiple excluded paths; single-path command uses one flag.

## Sync exclusions

- [x] Add `hk sync --exclude PATH --reason '...'`.
- [x] Allow repeated `--exclude` flags for multiple paths.
- [x] Require `--reason` when exclusions are present.
- [x] Reject excluded paths not present in git status.
- [x] Store excluded path list, reason, non-excluded hash, and excluded metadata in sync checkpoint events.
- [x] Make `sync --check` and `ready` pass only when non-excluded work is unchanged.
- [x] Render `## Sync exclusions` in handoff.

## Spec impact

- [x] Add structured `--spec-impact none|updated|not-needed` support.
- [x] Preserve `--no-spec-impact` as compatibility alias for `--spec-impact none`.
- [x] Add repeated `--spec-ref PATH` support.
- [x] Update handoff/status rendering for structured spec impact.

## Review ergonomics

- [x] Clarify docs/help: independent review preferred; fresh-context subagent is the minimum acceptable fallback.
- [x] Add `hk review prompt`.
- [x] Document future configurable review sources without implementing config.

## Status/help cleanup

- [x] Add `hk status` phase labels.
- [x] Further demote advanced `work`/`note`/`capture` surfaces in help/docs.

## Tests

- [x] Test excluded `.pi` path allows readiness when non-excluded work is unchanged.
- [x] Test source change after excluded sync makes readiness fail.
- [x] Test `sync --exclude` requires reason.
- [x] Test absent excluded path fails.
- [x] Test handoff renders sync exclusions.
- [x] Test structured spec impact and spec refs.
- [x] Test review prompt output and self-review warning.
- [x] Test status phase labels.

## Validation and dogfood

- [x] Run focused unit/e2e tests.
- [x] Run `mise run check`.
- [x] Run less-guided three-worker PR-sized dogfood in temp repos.
- [x] Capture dogfood study artifact.
- [x] Get independent/fresh-context review.
- [x] Run `mise run sync-check -- --plan-dir .ai/plans/2026-05-05-105158-hk2-final-polish-dogfood`.
