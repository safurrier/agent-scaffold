# HK2 review-default-on dogfood v5

Date: 2026-05-05

## Purpose

Validate the strengthened review-default-on guidance after the less-guided v4 run showed that workers did not naturally run `hk review prompt` or record review.

Worker prompts still asked them to begin by exploring HK, but explicitly said to complete the lifecycle and that they may dispatch/request an independent AI/tool or fresh-context subagent review if HK requires it. This tests whether the strengthened CLI/status/review prompt wording leads workers to at least follow the review prompt / explicit bypass path.

Temp repos:

- `/tmp/hk2-pr-sized-trials-v5/dread`
- `/tmp/hk2-pr-sized-trials-v5/foreman`
- `/tmp/hk2-pr-sized-trials-v5/obsidian-sync`

A `.pi/session.json` file was pre-created in each temp repo to keep sync exclusion behavior in scope.

## Outcomes

### dread

Changed:

- `src/dread/formatting.py`
- `tests/test_formatting.py`
- `tests/test_cli.py`

HK behavior:

- Used `hk start --plan --context`.
- Used structured `--spec-impact not-needed`.
- Ran `hk review prompt`.
- Could not obtain independent/fresh-context review in delegated worker environment.
- Recorded explicit `hk dangerously-skip review`.
- Used `hk sync --exclude .pi --reason ...`.
- Final readiness: `ready-with-dangerous-skips`.

### foreman

Changed:

- `tests/cli_config.rs`

HK behavior:

- Used `hk start --plan`.
- Used `hk review prompt`.
- Checked `hk review add --help`.
- Could not obtain independent/fresh-context review in delegated worker environment.
- Recorded explicit `hk dangerously-skip review`.
- Used `hk sync --exclude .pi --reason ...`.
- Final readiness: `ready-with-dangerous-skips`.

### obsidian-sync

Changed:

- `src/obsidian_sync/cli.py`
- `tests/test_cli.py`

HK behavior:

- Used `hk start --plan --context`.
- Used structured `--spec-impact not-needed`.
- Ran `hk review prompt`.
- Could not obtain independent/fresh-context review in delegated worker environment.
- Recorded explicit `hk dangerously-skip review`.
- Used `hk sync --exclude .pi --reason ...`.
- Final readiness: `ready-with-dangerous-skips`.

## Command summary

| Repo | HK commands | Non-zero commands | Review behavior | Sync behavior |
|---|---:|---:|---|---|
| dread | 30 | 5 | `review prompt` then dangerous review skip | `sync --exclude .pi` |
| foreman | 23 | 0 | `review prompt`, `review add --help`, then dangerous review skip | `sync --exclude .pi` |
| obsidian-sync | 24 | 0 | `review prompt` then dangerous review skip | `sync --exclude .pi` |

Dread's non-zero commands were validation/environment exploration and expected readiness failures before finalization, not HK syntax failures.

## Findings

### 1. Stronger review guidance worked for discovery

Unlike v4, all three workers ran `hk review prompt`. This is a material improvement.

### 2. Review still was not actually obtained

All three workers reported that the delegated-worker environment could not launch or obtain an independent AI/tool or fresh-context subagent review. They correctly avoided self-review and recorded `hk dangerously-skip review`.

This means the policy and bypass audit path are working, but the harness/tooling needs an easy way for workers to actually dispatch reviewer agents if we want fewer review skips.

### 3. `hk sync --exclude` became consistent

All three workers used `hk sync --exclude .pi --reason ...`. The explicit status/help guidance appears sufficient once workers are trying to complete readiness.

### 4. Structured spec impact improved

Dread and obsidian-sync used structured `--spec-impact not-needed`; foreman used structured `--spec-impact none`. The status/help nudges are working better.

## Recommendation

Keep the review-default-on wording. Next improvement should not loosen readiness; it should make reviewer dispatch easier.

Recommended future direction:

- Add scaffolding/instructions that explicitly say implementation agents may dispatch a fresh-context reviewer subagent.
- Consider an optional command or prompt-template integration that prints not only the review prompt, but a ready-to-run delegation snippet for the current harness.
- Keep `dangerously-skip review` as the auditable fallback when reviewer dispatch is unavailable.

## Copied artifacts

- `dogfood-v5-hk-commands.log`
- `dogfood-v5-dread-worker-report.md`
- `dogfood-v5-dread-handoff.md`
- `dogfood-v5-foreman-worker-report.md`
- `dogfood-v5-foreman-handoff.md`
- `dogfood-v5-obsidian-sync-worker-report.md`
- `dogfood-v5-obsidian-sync-handoff.md`
