---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area for the HK2 architecture parity refactor.
---

# Decisions — hk2-architecture-parity-refactor

## What Changed

- Planned a full ten-candidate architecture refactor instead of limiting pre-PR work to legacy isolation/readiness/rendering.
- Chose parity-driven sequencing: characterize behavior first, then extract one Module seam at a time, then run a focused parity gate before continuing.
- Pulled test fixtures and repo identity/state resolution forward as foundation chunks because they reduce risk and churn for the remaining extractions.
- Revised "fully deprecated legacy" to mean removed from `hk`, not compatibility-preserved:
  - `hk legacy plan` and `hk legacy sync-check` are deleted;
  - root `hk attach` is deleted;
  - normal HK2 commands do not silently route to legacy behavior;
  - scaffold/task-contract `mise run sync-check` remains supported through the slice-workflow CLI.

## Why

- The current HK2 behavior is ready, but the implementation has low Locality because lifecycle, ledger, readiness, rendering, capture, profiles, specs, and legacy compatibility are concentrated in broad Modules.
- A large structural refactor is acceptable only if each seam is parity-checked independently.
- Scaffold/task-contract users do not need `hk legacy`; their durable plan gate is `mise run sync-check` backed by the slice-workflow CLI, so removing `hk legacy` simplifies the HK2 Interface without breaking that gate.

## Where Reflected

- `SPEC.md` in this plan records success criteria and allowed legacy deprecation breaks.
- `IMPLEMENTATION.md` records the chunk-by-chunk parity plan and subagent rollout.
- `TODO.md` records execution tasks.

## Promotion

- No durable ADR yet. If implementation changes public deprecation behavior beyond runtime warnings/help hiding, update `docs/decisions/0009-harness-kit-lifecycle-first-cli.md` or add a new ADR before merge.
