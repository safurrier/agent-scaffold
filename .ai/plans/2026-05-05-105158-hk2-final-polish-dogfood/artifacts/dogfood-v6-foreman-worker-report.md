# Foreman HK Dogfood Worker Report

## Change made

- Added a test-only regression in `tests/cli_config.rs`:
  - `config_show_reports_invalid_config_without_failing`
  - The test writes an invalid TOML config, runs `foreman --config-show --config-file <path> --log-dir <path>`, and asserts the command succeeds while printing the config readout plus `config_parse_error:` / `invalid table header`.
- No production source files were changed.
- Existing untracked `.pi/` agent-local state was present before/throughout the slice and was not touched intentionally.

## Validation run

- `hk validate --target . --why 'Focused CLI/config regression coverage for --config-show reporting invalid TOML without exiting non-zero.' --kind test -- cargo test --test cli_config config_show_reports_invalid_config_without_failing -- --nocapture`
  - Result: pass
  - Evidence: `ev_20260505_131453_846236`
- `hk validate --target . --why 'Full CLI/config integration test file still passes after adding the config-show invalid TOML regression.' --kind test -- cargo test --test cli_config`
  - Result: pass
  - Evidence: `ev_20260505_131518_027846`

## HK commands tried

1. `/tmp/hk2-pr-sized-trials-v6/bin/hk --help`
   - Used to onboard to available lifecycle commands.
2. `/tmp/hk2-pr-sized-trials-v6/bin/hk status --help && /tmp/hk2-pr-sized-trials-v6/bin/hk start --help && /tmp/hk2-pr-sized-trials-v6/bin/hk validate --help`
   - Used to inspect command usage.
3. `/tmp/hk2-pr-sized-trials-v6/bin/hk status --target .`
   - Reported no active work and instructed `hk start`.
4. `/tmp/hk2-pr-sized-trials-v6/bin/hk start foreman-cli-config-test-only --plan 'Make a narrow test-only Rust change around existing Foreman CLI/config behavior, validate it with focused cargo tests, and record HK review/ready lifecycle evidence.' --target .`
   - Created work item `2026-05-05-131409-foreman-cli-config-test-only`.
5. `/tmp/hk2-pr-sized-trials-v6/bin/hk context --target . 'Repo guidance asks for feature branch and mise plan; branch already hk2-dogfood-v6-foreman. First mise plan attempt was blocked by untrusted .mise.toml. Slice will be test-only in tests/cli_config.rs around existing --config-show invalid config readout behavior.'`
   - Recorded durable context.
6. `/tmp/hk2-pr-sized-trials-v6/bin/hk decide --target . --no-spec-impact 'Add focused regression coverage for existing CLI/config readout behavior only; no product behavior or spec contract changes intended.'`
   - Recorded no-spec-impact decision.
7. `/tmp/hk2-pr-sized-trials-v6/bin/hk status --target .`
   - Showed validation, review, and sync still required; noted `.pi/` needed reconciliation/exclusion.
8. `/tmp/hk2-pr-sized-trials-v6/bin/hk validate --target . --why 'Focused CLI/config regression coverage for --config-show reporting invalid TOML without exiting non-zero.' --kind test -- cargo test --test cli_config config_show_reports_invalid_config_without_failing -- --nocapture`
   - Passed.
9. `/tmp/hk2-pr-sized-trials-v6/bin/hk validate --target . --why 'Full CLI/config integration test file still passes after adding the config-show invalid TOML regression.' --kind test -- cargo test --test cli_config`
   - Passed.
10. `/tmp/hk2-pr-sized-trials-v6/bin/hk review --help && /tmp/hk2-pr-sized-trials-v6/bin/hk review prompt --target .`
    - Printed the required fresh-context review prompt.
11. `/tmp/hk2-pr-sized-trials-v6/bin/hk dangerously-skip --help && /tmp/hk2-pr-sized-trials-v6/bin/hk dangerously-skip review --target . --reason 'HK requested a fresh-context reviewer/subagent, but this delegated environment exposes no independent review or fresh-context subagent tool and developer instructions prohibit launching subagents. Recording explicit bypass rather than self-review.'`
    - Explicitly bypassed review rather than self-reviewing.
12. `/tmp/hk2-pr-sized-trials-v6/bin/hk sync --help`
    - Inspected sync usage after status noted `.pi/`.
13. `/tmp/hk2-pr-sized-trials-v6/bin/hk sync --target . --exclude .pi --reason 'Pre-existing agent-local .pi state is outside this slice; only tests/cli_config.rs is an intentional repo change.'`
    - Recorded a synced checkpoint excluding `.pi/`.
14. `/tmp/hk2-pr-sized-trials-v6/bin/hk ready --target .`
    - Result: `ready-with-dangerous-skips`.
15. `/tmp/hk2-pr-sized-trials-v6/bin/hk handoff --target .`
    - Rendered the HK handoff.
16. `/tmp/hk2-pr-sized-trials-v6/bin/hk status --target .`
    - Final HK status: phase `ready`, readiness `ready-with-dangerous-skips`, sync `synced`.

## Other command mistake / friction

- Tried `mise run plan -- foreman-cli-config-test-only` because repo guidance requests a plan for meaningful work.
  - Result: failed before running because `.mise.toml` is not trusted in this temp checkout.
  - I did not run `mise trust`; I continued with HK lifecycle and focused `cargo test` validation.

## Review status

- HK review prompt required independent/fresh-context review.
- No independent AI/tool or fresh-context subagent mechanism was available in this delegated environment, and developer instructions explicitly prohibited launching subagents.
- Recorded explicit HK bypass with `hk dangerously-skip review ...`.
- Final readiness is therefore `ready-with-dangerous-skips`, not fully independently reviewed.

## Workflow friction / helpful guidance

- HK status guidance was useful: it clearly listed missing validation/review/sync checks and gave the `.pi/` sync exclusion hint.
- The review prompt was explicit that self-review does not count and that a dangerous skip is the correct fallback when no fresh-context reviewer is available.
- The repo-level `mise run plan` requirement conflicts with an untrusted `.mise.toml` in this temp checkout unless the worker is allowed to trust mise config.
