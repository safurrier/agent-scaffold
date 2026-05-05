# dread HK dogfood worker report

## Change made

Implemented a small user-visible message formatting fix:

- `src/dread/formatting.py`
  - `message_preview()` now collapses Discord message control whitespace (`tab`, `CR`, `LF`, `form-feed`, `vertical-tab`) into a single space.
  - This preserves ordinary spaces while preventing plain-text CLI rows from being split into extra columns or terminal lines.
- `tests/test_formatting.py`
  - Added focused formatter coverage for control-whitespace normalization and truncation after normalization.
- `tests/test_cli.py`
  - Added a `message list` plain-output regression test proving a message containing tab + CRLF renders as one tab-separated row: `id<TAB>preview`.

Edge case selected: `dread message list` and mention/inbox plain output are tab-separated, but prior previews only replaced `\n`. Message content with tabs could add fake columns, and `\r`/other control whitespace could disrupt terminal output.

## Validation run

Passing validations:

1. Focused local loop:
   - `uv run --with pytest python -m pytest tests/test_formatting.py tests/test_cli.py -k 'message_preview or message_list_plain_output' -v`
   - Result: `3 passed, 19 deselected`.
2. Lint/type/focused tests:
   - `uv run --extra dev ruff check src/dread/formatting.py tests/test_formatting.py tests/test_cli.py && uv run --extra dev ty check && uv run --extra dev python -m pytest tests/test_formatting.py tests/test_cli.py -k 'message_preview or message_list_plain_output' -v`
   - Result: ruff passed, ty passed, `3 passed, 19 deselected`.
   - HK evidence: `ev_20260505_110546_251746`.
3. Full offline unit suite:
   - `uv run --extra dev python -m pytest tests/ --ignore=tests/e2e -v`
   - Result: `168 passed, 1 warning`.
   - HK evidence: `ev_20260505_110628_012945`.

Validation command attempts that failed before finding the right invocation:

- `uv run pytest tests/test_formatting.py tests/test_cli.py -k 'message_preview or message_list_plain_output' -v`
  - Failed because the `pytest` entry point resolved to system Python 3.9, which cannot import `datetime.UTC`.
- `uv run --python 3.12 pytest tests/test_formatting.py tests/test_cli.py -k 'message_preview or message_list_plain_output' -v`
  - Same failure: `pytest` entry point still resolved to Python 3.9.
- `uv run python -m pytest tests/test_formatting.py tests/test_cli.py -k 'message_preview or message_list_plain_output' -v`
  - Failed because pytest was not installed in the project environment until using `--with pytest` or `--extra dev`.

## Every HK command tried

In order:

1. `/tmp/hk2-pr-sized-trials-v4/bin/hk --help`
   - Onboarded to available HK commands.
2. `/tmp/hk2-pr-sized-trials-v4/bin/hk status --help && /tmp/hk2-pr-sized-trials-v4/bin/hk init --help && /tmp/hk2-pr-sized-trials-v4/bin/hk start --help`
   - Explored startup/status flow.
3. `/tmp/hk2-pr-sized-trials-v4/bin/hk init --target . --json && /tmp/hk2-pr-sized-trials-v4/bin/hk status --target . --json`
   - Initialized local HK state and confirmed no active work.
4. `/tmp/hk2-pr-sized-trials-v4/bin/hk start message-format-edge --target . --plan 'Identify a narrow user-visible message formatting or CLI output edge case, implement code and focused tests, then validate relevant tests.' --context 'Working in temp dread checkout only; use HK to capture workflow evidence.' --json`
   - Started active work item `2026-05-05-110317-message-format-edge`.
5. `/tmp/hk2-pr-sized-trials-v4/bin/hk brief --target . && /tmp/hk2-pr-sized-trials-v4/bin/hk checks --target .`
   - Read repo/HK brief and available checks.
6. `/tmp/hk2-pr-sized-trials-v4/bin/hk sync --target . --json`
   - Recorded an initial sync checkpoint.
7. `/tmp/hk2-pr-sized-trials-v4/bin/hk plan --target . --set 'Normalize control whitespace (tabs, CR/LF, form-feed/vertical-tab) in message previews so tab-separated CLI rows stay single-line/single-column; add focused tests for formatter and message list output.' --json`
   - Mistake: `hk plan` has no `--set` option.
8. `/tmp/hk2-pr-sized-trials-v4/bin/hk plan --help`
   - Checked correct syntax.
9. `/tmp/hk2-pr-sized-trials-v4/bin/hk plan --target . --text 'Normalize control whitespace (tabs, CR/LF, form-feed/vertical-tab) in message previews so tab-separated CLI rows stay single-line/single-column; add focused tests for formatter and message list output.' --json`
   - Recorded refined implementation plan.
10. `/tmp/hk2-pr-sized-trials-v4/bin/hk validate --help`
    - Checked validation command syntax.
11. `/tmp/hk2-pr-sized-trials-v4/bin/hk validate --target . --kind check --why 'Focused lint, typecheck, and regression coverage for message preview/CLI output change' --shell "uv run --extra dev ruff check src/dread/formatting.py tests/test_formatting.py tests/test_cli.py && uv run --extra dev ty check && uv run --extra dev python -m pytest tests/test_formatting.py tests/test_cli.py -k 'message_preview or message_list_plain_output' -v" --json`
    - Recorded passing focused lint/type/test evidence.
12. `/tmp/hk2-pr-sized-trials-v4/bin/hk decide --help && /tmp/hk2-pr-sized-trials-v4/bin/hk note --help`
    - Explored decision/note syntax.
13. `/tmp/hk2-pr-sized-trials-v4/bin/hk decide --target . 'Preserve normal spaces but collapse control whitespace in previews instead of changing all whitespace, to keep user text mostly intact while protecting tab-separated CLI output.' --spec-impact not-needed --json`
    - Recorded implementation decision and spec impact.
14. `/tmp/hk2-pr-sized-trials-v4/bin/hk validate --target . --kind test --why 'Full offline unit suite after message preview formatting change' -- uv run --extra dev python -m pytest tests/ --ignore=tests/e2e -v`
    - Recorded passing full offline test evidence.
15. `/tmp/hk2-pr-sized-trials-v4/bin/hk sync --target . --json && /tmp/hk2-pr-sized-trials-v4/bin/hk ready --target . --json`
    - Sync passed; readiness failed because external-enough review was missing.
16. `/tmp/hk2-pr-sized-trials-v4/bin/hk note --target . --kind gap --text 'HK ready remains not-ready because external-enough review requires a separate reviewer/subagent, which this delegated worker was instructed not to launch.' --json`
    - Recorded review gap.
17. `/tmp/hk2-pr-sized-trials-v4/bin/hk status --target . --json`
    - Showed readiness still blocked on review and sync stale due untracked `.pi` local agent state.
18. `/tmp/hk2-pr-sized-trials-v4/bin/hk sync --target . --json && /tmp/hk2-pr-sized-trials-v4/bin/hk ready --target . --json`
    - After removing `.pi`, sync passed; readiness still failed only on missing external-enough review.

## Places I chose not to use HK

- File exploration/editing used the provided repo tools (`read`, `grep`, `find`, `edit`, `write`) because HK does not replace source inspection or code editing.
- I ran validation commands directly before `hk validate` to debug the Python/pytest invocation issue quickly, then recorded passing validations with HK.
- I used plain `git diff` / `git status` to inspect local source changes.
- I removed the untracked local `.pi/` agent-state directory with `rm -rf .pi` after HK status identified it as blocking sync freshness; it was not source code.

## HK workflow friction / helpful guidance

Helpful:

- `hk --help`, `hk brief`, and `hk checks` made the lifecycle model discoverable enough to start quickly.
- `hk ready` clearly identified missing review evidence.
- `hk status` specifically called out `.pi` as common agent-local state and explained why sync was stale.
- Validation evidence IDs and transcript paths are useful for handoff.

Friction:

- I guessed `hk plan --set`; the actual option is `--text`. The error was clear, and `hk plan --help` resolved it.
- `hk validate` emitted `VIRTUAL_ENV` mismatch warnings from an unrelated harness environment, even though commands ran correctly in the project `.venv`.
- HK readiness expects an external-enough review. This delegated worker was explicitly instructed not to launch reviewers/subagents, so readiness remains `not-ready` despite code validation passing.
- Native `uv run pytest` in this environment resolved a Python 3.9 pytest entry point; the reliable command was `uv run --extra dev python -m pytest ...`.
