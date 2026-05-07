# dread worker report

## Changed files
- `src/dread/formatting.py` — `message_preview()` now collapses any whitespace run (newlines, CRLF, tabs, repeated spaces) to a single space and trims edges before truncating. This keeps default tab-separated CLI previews single-line and tab-safe.
- `tests/test_formatting.py` — added focused tests for whitespace normalization, truncation after normalization, and unchanged plain short content.
- `tests/test_config_favorites.py` — changed an existing pytest regex string to a raw string so the profile lint check passes under current Ruff.

## HK profile resolution and checks seen
- Command: `/tmp/hk-profile-config-dogfood/bin/hk profile resolve --target . --json`
  - Resolved profile: `dread`
  - Reason: target matched configured longest path prefix
  - Config path: `/tmp/hk-profile-config-dogfood/harness.toml`
- Command: `/tmp/hk-profile-config-dogfood/bin/hk checks --target . --json`
  - `formatting-tests`: `uv run pytest tests/test_formatting.py -q` (agent should run directly; use for formatting helper changes)
  - `lint-changed`: `uv run ruff check src/ tests/` (agent should run directly)
  - Review guidance: `codex-core`, backend `codex`, dispatch hint `codex review --uncommitted`, rubric `core-quality`

## Validation commands
- Direct run: `uv run pytest tests/test_formatting.py -q`
  - First run exposed an incorrect test expectation for truncation length; fixed the expected string.
  - Final result: `3 passed in 0.01s`.
  - Recorded with HK: `hk validate --why 'Profile formatting-tests check for message preview formatting helper changes; observed direct run passed: 3 passed in 0.01s.' -- uv run pytest tests/test_formatting.py -q`
- Direct run: `uv run ruff check src/ tests/`
  - First run found the new import formatting issue plus a pre-existing `RUF043` in `tests/test_config_favorites.py`; both were fixed.
  - Final result: `All checks passed!`
  - Recorded with HK: `hk validate --why 'Profile lint-changed check for dread source and tests; observed direct run passed with all checks passed.' -- uv run ruff check src/ tests/`

## Review dispatch outcome
- Codex was available at `<USER_HOME>/.npm-global/bin/codex`.
- Attempting to pass the profile prompt with `codex review --uncommitted <prompt>` failed because this Codex version rejects combining `--uncommitted` and a prompt.
- Ran the dispatch hint as supported: `codex review --uncommitted`.
- Codex final review result: no discrete bugs found; the formatting change and tests are consistent with intended single-line message preview behavior.
- Recorded with HK: `hk review add --backend codex --reviewer codex-core --rubric core-quality ...` with disposition `accepted`.

## HK ready status
- Work ID: `2026-05-05-160911-dread-message-preview-config`
- Recorded HK plan, decision/spec reflection, validation evidence, Codex review, and sync checkpoint.
- `hk ready --target . --json`: `ready: true`, status `ready`.
- `hk handoff --target . --format markdown` rendered successfully.

## Friction
- `tests/test_formatting.py` did not exist even though the profile check targeted it, so I created it.
- `ruff check src/ tests/` flagged an unrelated existing non-raw regex in `tests/test_config_favorites.py`; I fixed that small lint issue to satisfy the configured profile check.
- Codex review could not accept the configured prompt together with `--uncommitted`; running `codex review --uncommitted` alone succeeded.
- Codex tried an extra test under a system Python 3.9 environment and hit project Python-version mismatch noise, but the profile-required `uv run` validation passed under the project environment.
