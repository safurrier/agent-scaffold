# HK2 Codex review tool dogfood v7

Date: 2026-05-05

## Purpose

Test whether harness-facing Codex review guidance moves workers from `dangerously-skip review` to an actual review record.

Single temp repo:

- `/tmp/hk2-pr-sized-trials-v7/dread`

## Outcome

Changed:

- `src/dread/formatting.py`
- `tests/test_formatting.py`

Behavior:

- `message_preview()` collapses whitespace runs before truncation so tabular CLI output is safer around embedded tabs/newlines/carriage returns.

Validation through HK:

- `uv run pytest tests/test_formatting.py -v` — pass.
- `uv run ruff check src/dread/formatting.py tests/test_formatting.py` — pass.

Review:

- Worker ran `hk review prompt`.
- Worker tried the HK-suggested Codex stdin form, `codex review --uncommitted -`; this failed in the installed Codex CLI with `the argument '--uncommitted' cannot be used with '[PROMPT]'`.
- Worker recovered by running `codex review --uncommitted`.
- Codex accepted the code/test change and only flagged unrelated `.pi/session.json` local state.
- Worker recorded review with `hk review add --backend codex --reviewer codex-review ...`.

Sync/readiness:

- Worker removed the first `.pi/session.json` artifact and ran `hk sync`/`hk ready`, but a later Codex/Pi monitor file appeared at `.pi/state/codex-pr-review-monitor.json` after the sync checkpoint.
- Parent check showed `not-ready` due stale sync from `.pi`.
- Parent remediated with `hk sync --exclude .pi --reason 'Codex/Pi review monitor state is agent-local...'`.
- Final parent readiness after constrained sync: `ready`.

## Findings

1. The tool-callable Codex direction works: the worker obtained and recorded an actual Codex review instead of using `dangerously-skip review`.
2. The exact `codex review --uncommitted -` hint was wrong for this installed Codex CLI. Use `codex review --uncommitted` as the default hint.
3. Review tooling can create agent-local `.pi` state after validation/review. HK should tell agents to re-run `hk status` after review and reconcile/remove/exclude agent-local state before final `ready`.

## Applied follow-up

- Replaced `codex review --uncommitted -` guidance with `codex review --uncommitted`.
- Added guidance to re-run `hk status` after review tools run.

## Copied artifacts

- `dogfood-v7-hk-commands.log`
- `dogfood-v7-dread-worker-report.md`
- `dogfood-v7-dread-handoff-before-parent-sync.md`
- `dogfood-v7-dread-handoff-after-sync.md`
- `dogfood-v7-dread-ready-after-sync.json`
