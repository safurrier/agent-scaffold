---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — hk2-final-polish-dogfood

## Problem

HK2 now has a coherent lifecycle happy path, but one more polish pass should address the remaining ergonomic gaps before broader real use:

- agent-local state such as `.pi/` still forces either a stale sync or a full dangerous sync skip;
- spec impact is recorded as mostly free text, which limits readiness/status guidance;
- workers know self-review does not count, but need an obvious acceptable fresh-context subagent path;
- `hk status` is useful but can be more phase-oriented;
- docs/help still need to keep the lifecycle path dominant over advanced compatibility surfaces;
- a less-guided dogfood run should verify discoverability without naming the new features.

## Requirements

### MUST

- Add one-shot explicit sync exclusions using `hk sync --exclude PATH --reason '...'`.
- Allow repeated `--exclude` flags for multiple paths.
- Require `--reason` whenever `--exclude` is used.
- Reject excluded paths that do not currently appear in git status.
- Store excluded paths, reason, non-excluded sync hash, and excluded-path metadata in the sync checkpoint event.
- Make readiness pass only if non-excluded work remains unchanged after an excluded sync checkpoint.
- Render excluded paths under `## Sync exclusions` in handoff, not under `## Dangerous skips`.
- Add structured spec-impact modes for `hk decide`:
  - `none`;
  - `updated`;
  - `not-needed`.
- Add optional repeated `--spec-ref PATH` for `hk decide`.
- Keep independent review preferred and explicitly define fresh-context subagent review as the minimum acceptable fallback.
- Add `hk review prompt` that prints a copy-paste fresh-context reviewer prompt for the active work.
- Add phase labels to `hk status`: `not-started`, `planning`, `implementing`, `finalizing`, `ready`.
- Further demote advanced `work`/`note`/`capture` surfaces in docs/help without removing compatibility.
- Run a less-guided three-worker PR-sized dogfood run in temp repos.

### SHOULD

- Keep `dangerously-skip sync` available for cases where even constrained exclusion is not appropriate, but prefer `hk sync --exclude` for known path-local churn.
- Preserve shell-first validation: HK records native command evidence and does not choose project validation commands.
- Keep `--no-spec-impact` compatible as an alias for structured `--spec-impact none` unless implementation complexity says otherwise.
- Make `hk review prompt` output clear that the implementation agent must not answer its own prompt.

## Constraints

- Do not implement persistent `.harnessignore` or `.harness/harness.toml` ignore config in this slice.
- Do not implement configurable review-source policy yet; document it as future direction.
- Do not loosen readiness to accept implementation-agent self-review.
- Do not remove advanced commands in this slice.
- Use temp/synthetic repos for dogfood, not originals.
- Do not read the forbidden Obsidian note: `<PRIVATE_VAULT_PATH> kit 2.0 refactor.md`.
