---
id: plan-implementation
title: Implementation Plan
description: >
  Parity-driven plan for implementing all ten HK2 architecture deepening opportunities.
---

# Implementation — hk2-architecture-parity-refactor

## Approach

Treat this as a sequence of small architecture migrations with a ratchet after each one:

1. Characterize current behavior with tests or snapshots.
2. Move code behind the new Module seam with minimal behavior changes.
3. Keep public CLI behavior and on-disk state compatible unless the step is an explicit legacy deprecation break.
4. Run the focused parity gate.
5. Commit that step before starting the next one.

The implementation order below mostly follows the ten architecture-review candidates, but pulls two foundation pieces forward: reusable test fixtures and repo identity/state resolution. That reduces churn and makes the rest of the parity checks cheaper.

## Parity Gate Levels

### Level 0 — per-edit smoke

Use while actively editing a chunk:

```bash
uv run ruff format <touched files>
uv run ruff check <touched files>
uv run ty check <touched files>
uv run pytest <focused tests> -q
```

### Level 1 — per-chunk focused parity gate

Run before committing each chunk:

```bash
uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q
```

If the chunk touches rendering, profiles, or legacy workflow, include the specific new tests added in that chunk even if they live elsewhere.

### Level 2 — milestone full gate

Run after chunks 4, 7, and final:

```bash
mise run check
```

### Level 3 — plan handoff gate

Run at the end, and after any meaningful plan artifact changes:

```bash
mise run sync-check -- --plan-dir .ai/plans/2026-05-05-194606-hk2-architecture-parity-refactor
```

## Baseline Characterization First

Before moving modules, add a small parity test harness that captures current behavior without overfitting timestamps/paths.

Target new tests/helpers:

```text
tests/support/hk2_repo.py                         # reusable git repo / temp state helpers
tests/unit/test_hk2_lifecycle_parity.py           # app-level lifecycle parity tests
tests/e2e/test_hk2_cli_parity.py                  # CLI command smoke/golden behavior
tests/unit/test_hk2_rendering_parity.py           # normalized handoff/review prompt tests
```

Characterize these workflows:

1. Minimal lifecycle happy path:
   - `hk start <slug> --plan ...`
   - `hk decide ... --spec-impact not-needed`
   - `hk validate --why ... -- python -c '...'`
   - `hk review add --backend codex --reviewer codex-review --rubric core-quality --summary ...`
   - `hk sync`
   - `hk ready --json`
   - `hk handoff`
2. Review-required failure path:
   - ready fails before review;
   - `hk status` suggests `hk review prompt` and warns self-review does not count.
3. Sync exclusion path:
   - `.pi/...` dirty state;
   - `hk sync --exclude .pi --reason ...`;
   - readiness passes while non-excluded diff is unchanged;
   - readiness fails after source changes.
4. Dangerous review skip path:
   - explicit skip yields `ready-with-dangerous-skips`.
5. Profile/config path:
   - `$HARNESS_KIT_CONFIG` inline profiles;
   - longest target prefix;
   - `hk checks --target` resolves profile;
   - review `prompt_file` loads.
6. Legacy removal path:
   - root help does not show `legacy` or `attach`;
   - `hk legacy ...` exits as an unknown command;
   - `hk attach ...` exits as an unknown command;
   - `hk status` accepts only HK2 lifecycle flags, not legacy workflow flags.

Normalization rules:

- Normalize timestamps, state directories, absolute temp paths, work IDs, and git SHAs.
- Assert stable JSON keys and statuses rather than byte-for-byte full output where timestamps are expected.
- For markdown handoff/review prompt, assert required sections and key guidance lines; use golden files only after normalizing volatile values.

## Chunk 1 — Test Seam and Repo Fixtures

**Maps to architecture candidate 8.**

Goal: add reusable repo/git fixtures and characterization tests before structural movement.

Files likely created/changed:

```text
tests/support/hk2_repo.py
tests/unit/test_hk2_lifecycle_parity.py
tests/e2e/test_hk2_cli_parity.py
tests/unit/test_hk2_rendering_parity.py
tests/unit/test_harness_kit_2.py
tests/unit/test_portable_workflow.py
```

Acceptance:

- Current implementation passes new parity tests before any extraction.
- Existing tests still pass.

Gate:

```bash
uv run pytest tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_rendering_parity.py -q
uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q
```

## Chunk 2 — Shared Repo Identity and State Resolution

**Maps to architecture candidate 10.**

Goal: extract shared git root, branch, remote, repo key, scope key, and target scope resolution into a low-level Module without changing HK2 or legacy storage policy.

Potential files:

```text
src/harness_toolkit/kit/state/repo.py
src/harness_toolkit/kit/state/paths.py
src/harness_toolkit/kit/local.py
src/harness_toolkit/kit/workflow.py
tests/unit/test_repo_state_resolution.py
```

Acceptance:

- HK2 local state paths do not change for existing targets.
- Legacy external/overlay state paths do not change.
- Scoped target behavior remains identical.

Gate:

```bash
uv run pytest tests/unit/test_repo_state_resolution.py tests/unit/test_harness_kit_2.py tests/e2e/test_harness_kit_rollout.py -q
```

## Chunk 3 — HK2 Lifecycle Application Module

**Maps to architecture candidate 1.**

Goal: introduce `LifecycleApp` or equivalent application Module. CLI commands call this Module, while existing lower-level functions can remain as forwarding shims during the migration.

Potential files:

```text
src/harness_toolkit/kit/app/lifecycle.py
src/harness_toolkit/kit/app/requests.py
src/harness_toolkit/kit/app/errors.py
src/harness_toolkit/kit/cli.py
src/harness_toolkit/kit/local.py
```

Acceptance:

- CLI remains shallow: commands construct request objects and delegate.
- Existing public functions continue to work for tests during transition.
- Minimal lifecycle parity workflow is unchanged.

Gate:

```bash
uv run pytest tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_harness_kit_2.py -q
```

## Chunk 4 — Typed Ledger/Event Seam

**Maps to architecture candidate 2.**

Goal: add typed event/evidence constructors/parsers over the existing JSONL format.

Potential files:

```text
src/harness_toolkit/kit/ledger/models.py
src/harness_toolkit/kit/ledger/store.py
src/harness_toolkit/kit/ledger/events.py
src/harness_toolkit/kit/local.py
tests/unit/test_hk2_ledger_events.py
```

Acceptance:

- Existing `events.jsonl` and `evidence.jsonl` fixtures/read paths still parse.
- New typed event writes produce the same JSON shape or an explicitly versioned compatible shape.
- Readiness, handoff, sync, and status consume typed event views rather than raw dict filtering where practical.

Gate:

```bash
uv run pytest tests/unit/test_hk2_ledger_events.py tests/unit/test_hk2_lifecycle_parity.py tests/unit/test_harness_kit_2.py -q
mise run check
```

## Chunk 5 — Readiness Policy Module

**Maps to architecture candidate 3.**

Goal: extract binary readiness rules and stable diagnostics from handoff/status presentation.

Potential files:

```text
src/harness_toolkit/kit/readiness/policy.py
src/harness_toolkit/kit/readiness/diagnostics.py
src/harness_toolkit/kit/readiness/messages.py
src/harness_toolkit/kit/app/status.py
src/harness_toolkit/kit/local.py
```

Acceptance:

- `hk ready --json` has the same external status/check IDs/messages unless intentionally improved with test updates.
- `hk status` next actions are generated from readiness diagnostics.
- Handoff readiness section uses the same diagnostics as `hk ready`.
- Review/self-review/sync exclusion edge cases remain covered.

Gate:

```bash
uv run pytest tests/unit/test_hk2_lifecycle_parity.py tests/unit/test_hk2_rendering_parity.py tests/unit/test_harness_kit_2.py -q
```

## Chunk 6 — Command Capture Adapters

**Maps to architecture candidate 4.**

Goal: separate process execution, git inspection, transcript persistence, and redaction behind Adapters used by evidence capture.

Potential files:

```text
src/harness_toolkit/kit/capture/recorder.py
src/harness_toolkit/kit/capture/process.py
src/harness_toolkit/kit/capture/git.py
src/harness_toolkit/kit/capture/redaction.py
src/harness_toolkit/kit/capture/transcripts.py
tests/unit/test_hk2_capture_adapters.py
```

Acceptance:

- Real CLI `hk validate` and `hk capture` behavior is unchanged.
- Redaction behavior remains unchanged for option-like secrets and raw log mode.
- Fake Adapter tests cover pass, fail, no-log, raw-log, and transcript paths without subprocess overhead.

Gate:

```bash
uv run pytest tests/unit/test_hk2_capture_adapters.py tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py -q
```

## Chunk 7 — Rendering Module

**Maps to architecture candidate 5.**

Goal: move handoff markdown, review prompt rendering, and materialized views out of lifecycle/local state code.

Potential files:

```text
src/harness_toolkit/kit/rendering/handoff.py
src/harness_toolkit/kit/rendering/review_prompt.py
src/harness_toolkit/kit/rendering/materialize.py
src/harness_toolkit/kit/rendering/presenters.py
src/harness_toolkit/kit/local.py
src/harness_toolkit/kit/cli.py
```

Acceptance:

- `hk handoff` sections and review prompt guidance remain stable.
- `hk handoff --format json` still returns the same dataclass JSON shape.
- `hk export` still writes generated views without creating substantive ledger events.

Gate:

```bash
uv run pytest tests/unit/test_hk2_rendering_parity.py tests/unit/test_harness_kit_2.py tests/e2e/test_hk2_cli_parity.py -q
mise run check
```

## Chunk 8 — Delete Legacy HK1 Plan-Artifact Commands

**Maps to architecture candidate 6, with the product decision to remove compatibility instead of isolating it.**

Goal: remove HK1 plan-artifact workflow commands from `hk` completely while preserving the independent scaffold/task-contract `mise run sync-check` path.

Potential files:

```text
src/harness_toolkit/kit/cli.py
src/harness_toolkit/kit/workflow.py          # delete if no longer imported
src/harness_toolkit/kit/state/repo.py        # shared helpers remain here
tests/e2e/test_hk_legacy_removed.py
tests/e2e/test_harness_kit_rollout.py
tests/unit/test_portable_workflow.py
README.md
SPEC.md
docs/portable-workflow.md
docs/harness-kit-lifecycle-design.md
docs/decisions/0009-harness-kit-lifecycle-first-cli.md
```

Acceptance:

- `hk legacy ...` is an unknown command.
- `hk attach ...` is an unknown command.
- Top-level `hk status` no longer switches into legacy workflow mode through `--mode`, `--state-root`, or `--profiles-dir`.
- Root help/docs teach HK2 lifecycle only.
- Tests that previously exercised portable plan-artifact workflow are removed or rewritten to HK2 lifecycle/profile behavior.
- `mise run sync-check` for scaffold plan artifacts remains unaffected because it uses the slice-workflow CLI.

Gate:

```bash
uv run pytest tests/e2e/test_hk_legacy_removed.py tests/e2e/test_harness_kit_rollout.py tests/unit/test_portable_workflow.py -q
```

## Chunk 9 — Profile Guidance Module Boundaries

**Maps to architecture candidate 7.**

Goal: split built-in profiles, user config loading, target binding resolution, and presentation while preserving guidance-only behavior.

Potential files:

```text
src/harness_toolkit/kit/profiles/models.py
src/harness_toolkit/kit/profiles/builtin.py
src/harness_toolkit/kit/profiles/config.py
src/harness_toolkit/kit/profiles/resolution.py
src/harness_toolkit/kit/profiles/presentation.py
src/harness_toolkit/kit/profiles.py          # compatibility re-export during transition
```

Acceptance:

- Existing imports keep working or are updated in one commit.
- Config lookup order remains `$HARNESS_KIT_CONFIG`, `$XDG_CONFIG_HOME/harness-toolkit/harness.toml`, `~/.config/harness-toolkit/harness.toml`.
- Longest-prefix target matching remains stable.
- `hk checks --target`, `hk profile resolve`, `hk profile show`, and profile review guidance output remain stable.

Gate:

```bash
uv run pytest tests/unit/test_portable_workflow.py tests/e2e/test_hk2_cli_parity.py -q
```

## Chunk 10 — Spec/Adoption Module

**Maps to architecture candidate 9.**

Goal: move optional spec source resolution, draft creation, outline extraction, and promotion dry-run into a dedicated Module.

Potential files:

```text
src/harness_toolkit/kit/specs/sources.py
src/harness_toolkit/kit/specs/drafts.py
src/harness_toolkit/kit/specs/outline.py
src/harness_toolkit/kit/specs/promotion.py
src/harness_toolkit/kit/local.py
src/harness_toolkit/kit/cli.py
```

Acceptance:

- Committed `SPEC.md` still wins over local draft.
- `hk spec init/status/outline/promote --dry-run` behavior remains stable.
- `hk decide --spec-ref PATH` continues to record structured spec references.

Gate:

```bash
uv run pytest tests/unit/test_harness_kit_2.py tests/e2e/test_hk2_cli_parity.py -q
```

## Chunk 11 — Final Integration Cleanup

Goal: remove stale forwarding shims that are no longer needed, update imports, refresh docs, and ensure module names teach the architecture.

Acceptance:

- No broad `local.py` god Module remains. It may remain as a compatibility facade, but high-level behavior lives in focused Modules.
- CLI remains a shallow Adapter.
- Public behavior is covered by parity tests and e2e smoke.
- Docs reflect the final module layout and legacy deprecation stance.

Gate:

```bash
mise run check
mise run sync-check -- --plan-dir .ai/plans/2026-05-05-194606-hk2-architecture-parity-refactor
```

## Subagent Rollout Plan

Run only after all chunks pass local gates.

### Rollout A — Fresh code review subagent

Task: inspect final diff for architecture regressions and accidental behavior changes. Focus on Module depth, CLI thinness, legacy deprecation, and shell-first boundaries.

Expected output:

- blockers;
- non-blocking refactors;
- confirmation that all ten architecture candidates were addressed.

### Rollout B — HK2 lifecycle dogfood subagent

Task: use `scripts/hk-dev` in a temp repo and execute the canonical HK2 lifecycle:

```bash
hk start rollout-smoke --plan 'Exercise lifecycle after architecture refactor'
hk context 'Temp repo smoke for HK2 lifecycle parity.'
hk decide 'No committed spec impact for temp smoke.' --spec-impact not-needed
hk validate --why 'Smoke command proves validation evidence still captures native commands' -- python -c 'print("ok")'
hk review prompt
hk review add --backend subagent --reviewer rollout-fresh-context --rubric core-quality --summary 'Smoke review accepted'
hk sync
hk ready --json
hk handoff
```

Expected output: final ready status and handoff summary.

### Rollout C — Profile/config dogfood subagent

Task: create a temp user `harness.toml` with two target bindings and inline checks/reviews; verify `hk profile resolve`, `hk checks --target`, and profile review guidance.

Expected output: resolved profile JSON and checks/reviews summary.

### Rollout D — Legacy removal subagent

Task: in a temp repo, verify removed legacy surfaces fail clearly: `hk legacy ...`, `hk attach ...`, and `hk status --mode overlay` should not work as legacy workflow entrypoints. Also verify `mise run sync-check` in this repo still uses the slice-workflow CLI and is unaffected.

Expected output: unknown-command evidence and unaffected slice-workflow sync-check result.

### Rollout E — Real-repo smoke subagents

Use temp clones/worktrees only. Suggested targets:

- `dread` — Python CLI profile-like repo.
- `foreman` — Rust CLI repo.
- `obsidian-sync` — daemon-ish Python repo.

Task: perform a tiny reversible change or no-op validation-only lifecycle, then run status/ready/handoff. Prefer no source edits unless needed; if edits happen, revert temp clone after capturing output.

Expected output: worker reports under this plan's artifacts directory.

## Final PR Readiness Checklist

- [ ] All chunks committed separately or intentionally squashed into coherent commits.
- [ ] Rollout reports saved under `artifacts/` and listed in `artifacts/manifest.yaml`.
- [ ] Fresh-context review recorded in `REVIEW.md`.
- [ ] Docs updated after final code layout.
- [ ] `mise run check` passed.
- [ ] `mise run sync-check -- --plan-dir .ai/plans/2026-05-05-194606-hk2-architecture-parity-refactor` passed.
