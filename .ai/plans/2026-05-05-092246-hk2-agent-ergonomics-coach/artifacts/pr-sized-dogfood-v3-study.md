# HK2 agent ergonomics PR-sized dogfood v3

Date: 2026-05-05

## Purpose

Validate the new HK2 ergonomics in realistic PR-sized worker tasks:

- `hk start <slug> --plan '...'`;
- optional `hk start --context '...'`;
- `hk status` as preflight / next-action coach;
- `hk dangerously-skip sync --reason '...'` for explicit local-agent sync risk;
- root `hk plan` no longer acting as a legacy plan fallback.

Workers ran in temporary clones only:

- `/tmp/hk2-pr-sized-trials-v3/dread`
- `/tmp/hk2-pr-sized-trials-v3/foreman`
- `/tmp/hk2-pr-sized-trials-v3/obsidian-sync`

The HK wrapper used the current checkout via `scripts/hk-dev`, preserving each worker's cwd so `--target .` resolved to the temp repo.

## Worker outcomes

### dread

Changed:

- `src/dread/formatting.py`
- `tests/test_formatting.py`

Behavior: `message_preview()` now normalizes tabs, carriage returns, and newline runs to a single space before truncation.

Validation through HK:

- `uv run pytest tests/test_formatting.py -v` — pass.
- `uv run ruff check src/dread/formatting.py tests/test_formatting.py` — pass.
- `uv run ty check` — pass.

Final readiness after parent collection snapshot:

- `ready-with-dangerous-skips`.
- Review skipped because no independent reviewer was available.
- Sync skipped for `.pi/session.json` agent-local state.

### foreman

Changed:

- `tests/cli_config.rs`

Behavior: added focused test coverage that malformed TOML with `foreman --config-show` reports `config_parse_error` and the TOML parse message.

Validation through HK:

- `cargo test --test cli_config config_show_reports_invalid_config_without_exiting_early` — pass.
- `cargo test --test cli_config` — pass, 17 tests.

Final readiness after parent collection snapshot:

- `ready-with-dangerous-skips`.
- Review skipped because no independent reviewer was available.
- Sync skipped for `.pi/session.json` agent-local state.

### obsidian-sync

Changed:

- `src/obsidian_sync/cli.py`
- `tests/test_cli.py`

Behavior: `obsidian-sync config --init` now uses the `SyncConfig` default interval (`60`) as the prompt default instead of hardcoded `300`; touched test helper path cleaned up after Ruff flagged an existing `S108` issue.

Validation through HK:

- `uv run -m pytest tests/test_cli.py::TestConfigCommand` — pass.
- `uv run ruff check src/obsidian_sync/cli.py tests/test_cli.py` — fail once on `S108`.
- `uv run ruff check src/obsidian_sync/cli.py tests/test_cli.py` — pass after cleanup.
- `uv run -m pytest tests/test_cli.py::TestConfigCommand` — pass again.

Final readiness after parent collection snapshot:

- `ready-with-dangerous-skips`.
- Review skipped because no independent reviewer was available.
- Sync skipped for `.pi/session.json` agent-local state.

## HK command behavior summary

Command counts from `/tmp/hk2-pr-sized-trials-v3/hk-commands.jsonl`:

| Repo | HK commands | Non-zero HK commands | Command mix |
|---|---:|---:|---|
| dread | 24 | 1 | help/status/start/context/decide/validate/review/sync/ready/handoff/dangerously-skip |
| foreman | 21 | 1 | help/start/status/decide/validate/sync/ready/review/dangerously-skip |
| obsidian-sync | 24 | 2 | help/start/status/context/decide/validate/review/sync/ready/handoff/dangerously-skip |

Non-zero commands were expected or useful:

- each worker intentionally hit `hk ready` failure after creating `.pi/session.json` post-sync;
- obsidian-sync captured one failed Ruff validation, fixed it, and reran validation.

## Findings

### 1. `hk start --plan` worked

All three workers discovered and used `hk start --plan` without syntax mistakes. One worker also used `--context` directly on start. Workers described the short slug + timestamped work ID model as clear.

This addressed the previous dogfood issue where plan records were inconsistent or late.

### 2. `hk status` worked as a coach

All three workers used `hk status` repeatedly. Reports say it identified missing decision, validation, review, and sync steps. After `.pi/session.json` was created, it surfaced stale sync and the agent-local `.pi` hint.

This addressed the previous issue where agents discovered readiness requirements only at final `hk ready`.

### 3. `dangerously-skip sync` was discoverable and used correctly

All three workers used `hk dangerously-skip sync --reason ...` after intentionally creating `.pi/session.json` after the sync checkpoint. The reasons were specific and risk-accepted rather than bland waivers.

Handoffs render sync skips under `## Dangerous skips`, and final `ready` returns `ready-with-dangerous-skips`.

### 4. Snapshot-tied sync skips are strict — maybe too strict for active `.pi`

Parent collection initially observed stale sync again after workers had reported ready. Likely cause: `.pi` agent-local state continued changing after the worker's sync skip / final ready. Because sync skips are tied to event sequence and diff hash, this correctly made the earlier skip stale.

This is honest but operationally sharp. Recommendation: document that `dangerously-skip sync` must be the last HK freshness action, or eventually design an explicit ignore policy for known agent-local paths. Do not silently ignore `.pi` in this slice.

Parent collection recorded a final sync skip per repo to capture stable handoffs. Those additional parent skips are visible in copied handoff artifacts.

### 5. Root legacy `hk plan` did not attract workers

No worker used root `hk plan` as a legacy artifact command. Workers used `start --plan`; none tried `hk legacy plan` or root `hk sync-check`.

### 6. Review independence behavior remained clear

All workers avoided self-review and used `hk dangerously-skip review` with explicit reasons when no independent reviewer was available. This preserves the policy-first review gate.

## Recommendation

Keep the implemented command shape. It materially improved agent behavior in this targeted rollout.

Follow-up candidates:

1. Add docs/help guidance that `dangerously-skip sync` is snapshot-tied and should be one of the final lifecycle actions if agent-local files keep changing.
2. Later, design explicit `.harnessignore` / harness config if repeated `.pi` churn remains too noisy.
3. Keep structured `--spec-ref` deferred; this rollout did not expose it as the blocking gap.

## Durable copied artifacts

Copied as top-level plan artifacts so they are reviewable under the repo artifact policy:

- `dogfood-v3-hk-commands.log`
- `dogfood-v3-dread-worker-report.md`
- `dogfood-v3-dread-handoff.md`
- `dogfood-v3-foreman-worker-report.md`
- `dogfood-v3-foreman-handoff.md`
- `dogfood-v3-obsidian-sync-worker-report.md`
- `dogfood-v3-obsidian-sync-handoff.md`
