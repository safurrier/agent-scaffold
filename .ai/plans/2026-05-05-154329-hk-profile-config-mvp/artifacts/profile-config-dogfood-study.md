# HK profile/config MVP dogfood study

Date: 2026-05-05

## Purpose

Validate user-level `harness.toml` with inline profiles/checks/reviews in temp clones. The test asks implementation workers to discover profile resolution and checks/review guidance without being handed repo-specific commands in the prompt.

Temp root:

- `/tmp/hk-profile-config-dogfood`

Repos:

- `dread`
- `foreman`

Config:

- `dogfood-profile-config.toml`

## Results

| Repo | Resolved profile | Checks used | Review guidance used | Final readiness |
|---|---|---|---|---|
| dread | `dread` | `uv run pytest tests/test_formatting.py -q`; `uv run ruff check src/ tests/` | `codex review --uncommitted`; recorded `hk review add --backend codex` | `ready` after parent sync exclusion for `.pi` |
| foreman | `foreman` | `cargo test --test cli_config`; `cargo fmt --check` | `codex review --uncommitted`; recorded `hk review add --backend codex` | `ready` after parent sync exclusion for `.pi` |

## Dread change

Changed:

- `src/dread/formatting.py`
- `tests/test_formatting.py`
- `tests/test_config_favorites.py` (Ruff raw-regex cleanup needed by profile lint)

Validation:

- `uv run pytest tests/test_formatting.py -q` — pass.
- `uv run ruff check src/ tests/` — pass.

Review:

- Codex review completed and reported no discrete bugs.
- Worker recorded an accepted review with `hk review add --backend codex --reviewer codex-core --rubric core-quality ...`.

## Foreman change

Changed:

- `src/cli.rs`
- `tests/cli_config.rs`

Validation:

- `cargo test --test cli_config` — pass.
- `cargo fmt --check` — pass.

Review:

- Codex review completed and found no correctness, compatibility, or test reliability issues.
- Worker recorded an accepted review with `hk review add --backend codex --reviewer codex-core --rubric core-quality ...`.

## Findings

1. `hk profile resolve --target . --json` worked and gave agents the intended profile.
2. `hk checks --target . --json` correctly used the resolved profile when `--profile` was omitted.
3. Inline profile checks lined up with the expected repo validation loops from previous dogfood:
   - dread: focused pytest + ruff;
   - foreman: focused `cargo test --test cli_config` + `cargo fmt --check`.
4. Inline profile reviews were useful: both workers used the Codex dispatch hint and recorded `hk review add` instead of dangerous review skip.
5. Codex/Pi review monitor state still appears under `.pi` after review/ready. Parent remediated with explicit `hk sync --exclude .pi --reason ...`, and both repos reached `ready`.

## Follow-up considerations

- The profile review guidance works without structured backend adapters.
- The `.pi` state behavior reinforces that profile/config should not silently ignore paths; status/sync exclusion remains the correct explicit path.
- Repo-level `.harness/harness.toml` can remain deferred.
