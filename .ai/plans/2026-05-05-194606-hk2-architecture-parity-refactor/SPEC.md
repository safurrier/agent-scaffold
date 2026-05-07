---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for the HK2 architecture parity refactor.
---

# Specification — hk2-architecture-parity-refactor

## Problem

HK2 now has the desired product behavior, but the implementation is concentrated in a few broad modules. `local.py` mixes lifecycle orchestration, ledger JSONL, git inspection, command capture, redaction, sync freshness, readiness policy, status coaching, handoff rendering, review prompt generation, and optional spec handling. `profiles.py` now mixes profile data, config loading, target resolution, prompt-file IO, and presentation. Legacy HK1 plan-artifact compatibility is marked deprecated, but pieces still leak through top-level command paths.

We want to implement all ten architecture deepening opportunities from the architecture review without regressing HK2 behavior. The key requirement is a parity-driven sequence: before each extraction, characterize the current behavior; after each extraction, prove behavior is still equivalent or explicitly document an intended deprecation break.

## Success Criteria

- HK2 public lifecycle behavior remains stable across the full refactor:
  - `hk start --plan`, `hk context`, `hk plan`, `hk decide`, `hk validate`, `hk review prompt`, `hk review add`, `hk sync`, `hk sync --exclude`, `hk ready`, `hk status`, `hk handoff`, and `hk export` keep their documented behavior.
- Existing user-level profile/config MVP behavior remains stable:
  - config lookup order;
  - inline profiles;
  - longest-prefix target matching;
  - `hk profile resolve`;
  - `hk checks --target` default profile resolution;
  - lightweight review guidance and `prompt_file` loading.
- Legacy plan-artifact commands are fully removed from `hk`:
  - `hk legacy plan`, `hk legacy sync-check`, and `hk attach` are deleted;
  - normal HK2 command paths do not carry legacy-only flags;
  - normal help/docs do not teach legacy as a starting point;
  - scaffold/task-contract `mise run sync-check` remains available through the slice-workflow CLI, not through `hk`.
- The refactor lands as small, parity-checked commits/chunks. Each chunk must be reversible and reviewable.
- Subagent rollout runs after the full refactor and exercises HK2 lifecycle, profile/config, legacy compatibility, and code architecture review in fresh contexts.

## Requirements

### MUST

- Add/strengthen characterization tests before moving behavior behind a new Module seam.
- Preserve on-disk HK2 ledger JSONL compatibility unless a migration test and explicit decision are added.
- Preserve generated handoff/review prompt semantics, with golden/snapshot-style tests where feasible.
- Keep HK shell-first: validation commands remain native shell commands captured by HK, not selected or executed by profiles automatically.
- Keep profiles guidance-only. Do not add review/check orchestration as part of this refactor.
- Delete `hk legacy plan`, `hk legacy sync-check`, `hk attach`, and the portable plan-artifact workflow code from `hk`.
- Run the focused parity gate after every chunk and the full gate after the final chunk.
- Use fresh-context review/subagents before PR once the full refactor is complete.

### SHOULD

- Prefer moving code with minimal behavior edits over rewriting logic during extraction.
- Keep old public functions as forwarding shims during intermediate chunks when that reduces churn.
- Introduce dataclasses/enums for typed internal events while continuing to read existing dict-shaped JSONL records.
- Make CLI commands thinner Adapters over application Modules.
- Make failure messages and status guidance live in presentation/message Modules after policy extraction.
- Add repo/git fixtures to reduce subprocess-heavy tests, but keep e2e smoke coverage for CLI wiring.

### MUST NOT

- Reintroduce `hk run` or make HK a task runner.
- Silently ignore `.pi` or other agent-local paths; sync exclusions must remain explicit evidence.
- Count implementation-agent self-review as review evidence.
- Delete scaffold/task-contract `mise run sync-check`; that gate belongs to the slice-workflow CLI and remains supported.
- Change current scaffold `mise run sync-check` behavior.

## Explicitly Intended Deprecation Breaks

These are required behavior changes and must be reflected in tests/docs:

- Delete `hk legacy` command group entirely.
- Delete root `hk attach`.
- Delete legacy-only flags from top-level HK2 commands, especially `hk status --mode/--state-root/--profiles-dir` fallback behavior.
- Delete `src/harness_toolkit/kit/workflow.py` or leave only a private migration-free module if another non-legacy path still needs shared helpers.

## Constraints

- Current branch: `feat/harness-kit-2-ledger-assistant`.
- Use `scripts/hk-dev` for dogfood against temp repos so the current checkout's HK is used while preserving caller cwd.
- Use temp clones/worktrees for rollout dogfood; do not mutate original external repos.
- Run repo gates through the stable contract:
  - `mise run check`
  - `mise run sync-check -- --plan-dir .ai/plans/2026-05-05-194606-hk2-architecture-parity-refactor`
- Commit plan artifacts only when they are reviewable and manifest-valid.
