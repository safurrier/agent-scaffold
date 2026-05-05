# HK2 review dispatch hint dogfood v6

Date: 2026-05-05

## Purpose

Test one lightweight improvement after v5: make `hk review prompt` and `hk status` explicitly say that if the harness has a fresh-context review mechanism, the implementation agent should dispatch the prompt to it now.

Single temp repo:

- `/tmp/hk2-pr-sized-trials-v6/foreman`

## Outcome

Changed:

- `tests/cli_config.rs`

Behavior tested:

- `foreman --config-show` succeeds with invalid TOML and reports config readout + parse error details.

Validation through HK:

- `cargo test --test cli_config config_show_reports_invalid_config_without_failing -- --nocapture` — pass.
- `cargo test --test cli_config` — pass.

HK lifecycle:

- Used `hk start --plan`.
- Used `hk context`.
- Used `hk decide --no-spec-impact`.
- Used `hk validate` with rationale.
- Ran `hk review prompt`.
- Did not obtain review: worker reported no independent AI/tool or fresh-context subagent mechanism was available in that delegated environment, and developer instructions prohibited launching subagents.
- Recorded explicit `hk dangerously-skip review` rather than self-review.
- Used `hk sync --exclude .pi --reason ...`.
- Final readiness: `ready-with-dangerous-skips`.

## Finding

The dispatch hint made the expected action clearer, but it did not create reviewer availability. The worker did run `hk review prompt` and explicitly said it would have dispatched if a fresh-context review mechanism were available. It then used the auditable dangerous review skip.

Conclusion: wording is now good enough. The remaining improvement is harness-level reviewer dispatch ergonomics, not HK policy text.

## Copied artifacts

- `dogfood-v6-hk-commands.log`
- `dogfood-v6-foreman-worker-report.md`
- `dogfood-v6-foreman-handoff.md`
