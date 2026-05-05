# HK2 final polish less-guided dogfood v4

Date: 2026-05-05

## Purpose

Validate the final-polish HK2 changes in a less-guided PR-sized dogfood run. Workers were told only to use HK and begin by exploring the CLI. The prompt did not name `sync --exclude`, structured spec impact, `review prompt`, or status phase labels.

Temp repos:

- `/tmp/hk2-pr-sized-trials-v4/dread`
- `/tmp/hk2-pr-sized-trials-v4/foreman`
- `/tmp/hk2-pr-sized-trials-v4/obsidian-sync`

A `.pi/session.json` file was pre-created in each temp repo to simulate local agent state without telling workers which HK feature should handle it.

## Outcomes

### dread

Changed:

- `src/dread/formatting.py`
- `tests/test_formatting.py`
- `tests/test_cli.py`

Validation through HK:

- focused lint/typecheck/regression shell command — pass;
- full offline unit suite — pass (`168 passed, 1 warning`).

HK behavior:

- Used `hk start --plan --context`.
- Used structured `--spec-impact not-needed`.
- Did not discover `hk sync --exclude`; ran plain `hk sync`, leaving readiness stale because `.pi` was present.
- Did not discover `hk review prompt`; stopped at missing external-enough review.

### foreman

Changed:

- `src/cli.rs`
- `tests/cli_config.rs`

Validation through HK:

- focused CLI/config regression — pass;
- `cargo fmt --check` — pass;
- full `cli_config` integration test — pass.

HK behavior:

- Used `hk start --plan --context`.
- Used compatibility `--no-spec-impact` rather than structured mode.
- Discovered and used `hk sync --exclude .pi --reason ...` successfully.
- Did not discover `hk review prompt`; stopped at missing external-enough review.

### obsidian-sync

Changed:

- `src/obsidian_sync/config.py`
- `src/obsidian_sync/cli.py`
- `tests/test_config.py`
- `tests/test_cli.py`

Validation through HK:

- focused malformed config tests — pass;
- `mise run check` — failed because mise config was not trusted;
- direct Ruff on touched files — failed on pre-existing test `S108` findings;
- repo lint scope (`src`) — pass;
- typecheck (`src`) — pass;
- full non-e2e suite — pass;
- Ruff format check on changed files — pass.

HK behavior:

- Used `hk start --plan` and later `hk context`.
- Used compatibility `--no-spec-impact` rather than structured mode.
- Discovered and used `hk sync --exclude .pi --reason ...` successfully.
- Did not discover `hk review prompt`; stopped at missing external-enough review.

## Command summary

| Repo | HK commands | Non-zero commands | Notes |
|---|---:|---:|---|
| dread | 25 | 3 | One guessed old `hk plan --set`; two `ready` failures due review + stale `.pi` sync. |
| foreman | 18 | 0 | Found `sync --exclude`; no readiness run by worker, parent readiness showed missing review only. |
| obsidian-sync | 24 | 3 | Captured two useful failed validations; found `sync --exclude`; parent readiness showed missing review only. |

## Findings

### 1. `hk start --plan` is naturally discoverable

All three workers used `hk start --plan`. Two used `--context` at start; one used `hk context` later. This confirms the previous ergonomics slice held up without targeted prompting.

### 2. `hk sync --exclude` is discoverable for some workers, but not universal

Foreman and obsidian-sync found and used `hk sync --exclude .pi --reason ...` correctly. Dread did not; it ran plain `hk sync` and remained stale. Status did include a concrete suggestion with `hk sync --exclude .pi --reason ...`, but the worker did not follow it.

Recommendation applied after the run: keep the status sync guidance, and consider whether the wording should make `sync --exclude` the first suggestion when only common agent-local paths are dirty.

### 3. Structured spec impact is only partly discoverable

Dread used `--spec-impact not-needed`. Foreman and obsidian-sync used compatibility `--no-spec-impact`. That is acceptable because compatibility was intentionally preserved, but docs/help should continue nudging structured modes.

### 4. `hk review prompt` was not discovered

No worker used `hk review prompt`. Workers stopped at missing review or noted they were not allowed/able to launch independent review. This suggests `hk status` should mention `hk review prompt` directly in the review next action.

Recommendation applied after the run: status review action now says to use `hk review prompt` to get a fresh-context reviewer prompt, then record with `hk review add`.

### 5. Phase labels are useful but mostly background

Parent-collected status showed `phase: finalizing` for all three workers, which is correct. Worker reports focused more on next actions than phase names. Keep phase labels; they are useful for machine-readable state and future UI, even if not highlighted in prose reports.

## Recommendation

Keep the final-polish features. The less-guided run shows:

- the main lifecycle happy path is discoverable;
- constrained sync exclusions are useful and discoverable by most workers;
- status needs to advertise review prompts more directly;
- compatibility `--no-spec-impact` is still used, so structured spec impact should remain additive rather than breaking.

## Copied artifacts

- `dogfood-v4-hk-commands.log`
- `dogfood-v4-dread-worker-report.md`
- `dogfood-v4-dread-handoff.md`
- `dogfood-v4-foreman-worker-report.md`
- `dogfood-v4-foreman-handoff.md`
- `dogfood-v4-obsidian-sync-worker-report.md`
- `dogfood-v4-obsidian-sync-handoff.md`
