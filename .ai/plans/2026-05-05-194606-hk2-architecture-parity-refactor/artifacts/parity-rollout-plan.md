# HK2 Architecture Parity Rollout Plan

## Purpose

This artifact summarizes the parity strategy for the full ten-candidate HK2 architecture refactor. The detailed execution plan lives in `../IMPLEMENTATION.md`.

## Core Ratchet

For every architecture chunk:

1. Add or confirm characterization coverage for current behavior.
2. Move one Module seam.
3. Preserve public behavior unless the chunk is an explicit legacy deprecation break.
4. Run the focused parity gate.
5. Commit before starting the next chunk.

No chunk should combine a behavior change, a rendering rewrite, and a storage/schema change unless the tests make that combination unavoidable.

## Behavior Areas to Preserve

- HK2 lifecycle commands.
- Readiness status and check IDs.
- Review-required-by-default behavior.
- Sync checkpoint and sync exclusion safety.
- Handoff and review prompt semantics.
- User config/profile resolution.
- Complete removal of `hk legacy plan`, `hk legacy sync-check`, and `hk attach` from the HK CLI while keeping scaffold `mise run sync-check` unaffected.
- Existing scaffold `mise run sync-check` behavior.

## Required Intentional Change

Legacy HK1 plan-artifact commands are removed from `hk`:

- `hk legacy ...` is an unknown command;
- `hk attach ...` is an unknown command;
- legacy fallback paths are removed from root HK2 commands.

Compatibility is measured at `hk legacy ...`, not at old root-level flag leakage.

## Subagent Rollout Matrix

| Rollout | Purpose | Expected proof |
|---|---|---|
| Fresh code review | Find architecture regressions and accidental behavior changes | Reviewer report with blockers/non-blockers |
| HK2 lifecycle dogfood | Exercise lifecycle in temp repo through `scripts/hk-dev` | Ready JSON + handoff |
| Profile/config dogfood | Exercise user config, target resolution, checks, reviews | Resolution/checks JSON |
| Legacy removal | Exercise removed HK1 command surfaces | Unknown-command output + successful independent `mise run sync-check` |
| Real-repo smoke | Exercise temp clones of representative repos | Worker reports and final readiness/status |

## Final Evidence Bundle

Expected artifacts after implementation:

- `architecture-review-report.md`
- `hk2-lifecycle-rollout.md`
- `profile-config-rollout.md`
- `legacy-removal-rollout.md`
- `real-repo-rollout-summary.md`
- focused validation logs if needed
