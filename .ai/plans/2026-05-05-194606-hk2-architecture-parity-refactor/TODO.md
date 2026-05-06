---
id: plan-todo
title: Task List
description: >
  Checkable tasks for the parity-driven HK2 architecture refactor.
---

# TODO — hk2-architecture-parity-refactor

## Planning

- [x] Cut slice with `mise run plan -- hk2-architecture-parity-refactor`.
- [x] Convert architecture-review suggestions into a parity-driven implementation plan.
- [x] Confirm final implementation order with Alex before touching source code.

## Chunk 1: Test Seam and Repo Fixtures

- [x] Add reusable HK2 temp repo/test helpers.
- [x] Add lifecycle parity tests for happy path, missing review, sync exclusions, dangerous skips, profile/config, and legacy removal expectations.
- [x] Run focused parity gate.
- [x] Commit chunk 1.

## Chunk 2: Shared Repo Identity and State Resolution

- [x] Extract common repo identity/state path helpers.
- [x] Preserve HK2 local state paths.
- [x] Preserve legacy external/overlay state paths.
- [x] Add/adjust tests for scoped target behavior.
- [x] Run focused parity gate.
- [x] Commit chunk 2.

## Chunk 3: HK2 Lifecycle Application Module

- [x] Introduce lifecycle application Module/request objects.
- [x] Make CLI lifecycle commands delegate through the Module.
- [x] Keep compatibility shims where useful during migration.
- [x] Run focused parity gate.
- [x] Commit chunk 3.

## Chunk 4: Typed Ledger/Event Seam

- [x] Add typed lifecycle event/evidence models and parsers.
- [x] Keep JSONL on-disk compatibility.
- [x] Move consumers away from raw dict filtering where practical.
- [x] Run focused parity gate plus `mise run check`.
- [x] Commit chunk 4.

## Chunk 5: Readiness Policy Module

- [x] Extract readiness diagnostics and binary policy.
- [x] Move human-facing wording into message/presentation layer.
- [x] Ensure `hk ready`, `hk status`, and handoff use the same diagnostics.
- [x] Run focused parity gate.
- [x] Commit chunk 5.

## Chunk 6: Command Capture Adapters

- [x] Extract process runner, git inspector, redactor, transcript store, and evidence recorder.
- [x] Add fake-adapter tests for pass/fail/no-log/raw-log behavior.
- [x] Preserve CLI `hk validate` / `hk capture` behavior.
- [x] Run focused parity gate.
- [x] Commit chunk 6.

## Chunk 7: Rendering Module

- [x] Move handoff rendering to focused rendering Module.
- [x] Move review prompt rendering to focused rendering Module.
- [x] Move materialized view generation out of lifecycle state code.
- [x] Add/refresh normalized rendering parity tests.
- [x] Run focused parity gate plus `mise run check`.
- [x] Commit chunk 7.

## Chunk 8: Delete Legacy HK1 Plan-Artifact Commands

- [x] Delete `hk legacy` command group.
- [x] Delete root `hk attach`.
- [x] Delete legacy-only top-level `hk status` fallback flags.
- [x] Delete or fully detach `src/harness_toolkit/kit/workflow.py` after shared repo helpers move elsewhere.
- [x] Verify focused HK2/removed-legacy tests pass; final `mise run sync-check` remains in final gates.
- [x] Run focused parity gate.
- [x] Commit chunk 8.

## Chunk 9: Profile Guidance Module Boundaries

- [x] Split profile models into a package boundary while preserving the catalog facade.
- [x] Keep existing imports working or update all imports in one commit.
- [x] Preserve config lookup order and longest-prefix matching.
- [x] Preserve checks/review guidance output.
- [x] Run focused parity gate.
- [x] Commit chunk 9.

## Chunk 10: Spec/Adoption Module

- [x] Move spec source resolution, draft creation, outline extraction, and promotion dry-run into a spec Module.
- [x] Preserve committed `SPEC.md` precedence.
- [x] Preserve `hk spec *` CLI behavior.
- [x] Run focused parity gate.
- [ ] Commit chunk 10.

## Chunk 11: Final Integration Cleanup

- [ ] Remove stale forwarding shims that are no longer needed.
- [ ] Update docs for final module layout and legacy deprecation stance.
- [ ] Run `mise run check`.
- [ ] Run plan `sync-check`.
- [ ] Commit final cleanup/docs.

## Subagent Rollout

- [ ] Run fresh code review subagent.
- [ ] Run HK2 lifecycle dogfood subagent in temp repo.
- [ ] Run profile/config dogfood subagent in temp repo.
- [ ] Run legacy removal subagent in temp repo.
- [ ] Run real-repo smoke subagents in temp clones/worktrees.
- [ ] Save reports under this plan's `artifacts/` directory.
- [ ] Update `artifacts/manifest.yaml`.
- [ ] Address blockers or explicitly defer non-blocking findings.

## PR Prep

- [ ] Final staged diff audit.
- [ ] Final validation evidence recorded in `VALIDATION.md`.
- [ ] Fresh-context review recorded in `REVIEW.md`.
- [ ] Push branch.
- [ ] Open/update PR after review and validation are clean.
