# Foreman HK dogfood worker report

## Change made

- Added a focused test-only regression in `tests/cli_config.rs`:
  - `config_show_handles_invalid_config_without_exiting_early`
  - The test writes malformed TOML to a temp `config.toml`, runs `foreman --config-show --config-file <path> --log-dir <path>`, and verifies the command succeeds while surfacing `config_parse_error`, the TOML parse message, and the doctor next-step guidance.
- No production source code was changed.
- `SPEC.md` impact: none. This documents existing CLI repair/readout behavior already implemented through `load_repair_config`.

## Validation run

All validations were recorded through HK:

1. `cargo test --test cli_config config_show_handles_invalid_config_without_exiting_early`
   - HK evidence: `ev_20260505_123836_221983`
   - Result: pass
2. `cargo fmt --check`
   - HK evidence: `ev_20260505_123859_168541`
   - Result: pass
3. `cargo test --test cli_config`
   - HK evidence: `ev_20260505_123906_913136`
   - Result: pass, 17 tests passed

## Review status

- HK review prompt was generated.
- I could not obtain an independent AI/tool or fresh-context subagent review from this delegated worker environment, and implementation-agent self-review does not satisfy HK.
- Recorded explicit HK bypass:
  - `hk dangerously-skip review --reason 'No independent AI/tool reviewer or fresh-context subagent is available in this delegated worker; implementation self-review is not acceptable, so recording explicit bypass per HK guidance.' --target .`
- Final readiness: `ready-with-dangerous-skips`.

## HK commands tried

No HK command failed due to a syntax mistake. The commands below include onboarding/help exploration and lifecycle commands:

1. `/tmp/hk2-pr-sized-trials-v5/bin/hk --help`
2. `/tmp/hk2-pr-sized-trials-v5/bin/hk status --help`
3. `/tmp/hk2-pr-sized-trials-v5/bin/hk start --help`
4. `/tmp/hk2-pr-sized-trials-v5/bin/hk validate --help`
5. `/tmp/hk2-pr-sized-trials-v5/bin/hk status --target .`
6. `/tmp/hk2-pr-sized-trials-v5/bin/hk brief --target .`
7. `/tmp/hk2-pr-sized-trials-v5/bin/hk review --help`
8. `/tmp/hk2-pr-sized-trials-v5/bin/hk ready --help`
9. `/tmp/hk2-pr-sized-trials-v5/bin/hk start cli-config-focused-test --plan 'Pick a narrow CLI/config behavior from existing Rust tests/source, implement a small code+test or test-only change, validate with focused cargo tests, then complete HK readiness with review recorded or explicit bypass.' --target .`
10. `/tmp/hk2-pr-sized-trials-v5/bin/hk status --target .`
11. `/tmp/hk2-pr-sized-trials-v5/bin/hk context 'Existing CLI repair paths already exercise invalid TOML for doctor/setup; config_readout also uses load_repair_config but lacked focused coverage that --config-show stays available and reports config_parse_error.' --target .`
12. `/tmp/hk2-pr-sized-trials-v5/bin/hk decide 'Add focused CLI config-show regression coverage for invalid TOML; this documents existing repair/readout behavior and has no product spec impact.' --spec-impact none --target .`
13. `/tmp/hk2-pr-sized-trials-v5/bin/hk validate --why 'Focused CLI config-show regression for invalid TOML readout' --kind test --target . -- cargo test --test cli_config config_show_handles_invalid_config_without_exiting_early`
14. `/tmp/hk2-pr-sized-trials-v5/bin/hk validate --why 'Formatting check for edited Rust test file' --kind lint --target . -- cargo fmt --check`
15. `/tmp/hk2-pr-sized-trials-v5/bin/hk validate --why 'Full cli_config integration coverage after adding config-show invalid TOML regression' --kind test --target . -- cargo test --test cli_config`
16. `/tmp/hk2-pr-sized-trials-v5/bin/hk review prompt --target .`
17. `/tmp/hk2-pr-sized-trials-v5/bin/hk review add --help`
18. `/tmp/hk2-pr-sized-trials-v5/bin/hk dangerously-skip --help`
19. `/tmp/hk2-pr-sized-trials-v5/bin/hk sync --help`
20. `/tmp/hk2-pr-sized-trials-v5/bin/hk dangerously-skip review --reason 'No independent AI/tool reviewer or fresh-context subagent is available in this delegated worker; implementation self-review is not acceptable, so recording explicit bypass per HK guidance.' --target .`
21. `/tmp/hk2-pr-sized-trials-v5/bin/hk sync --exclude .pi --reason 'Exclude pre-existing agent-local .pi state; lifecycle change is limited to tests/cli_config.rs.' --target .`
22. `/tmp/hk2-pr-sized-trials-v5/bin/hk ready --target .`
23. `/tmp/hk2-pr-sized-trials-v5/bin/hk handoff --target .`

## Workflow friction / helpful guidance

- Helpful: `hk status` clearly listed missing lifecycle pieces and suggested exact next actions.
- Helpful: `hk review prompt` produced a complete reviewer handoff including plan, context, validation evidence, and changed paths.
- Friction: In this delegated-worker setup I could not actually dispatch an independent reviewer, so HK's dangerous review skip path was necessary.
- Friction: The repo had pre-existing untracked `.pi/` agent-local state. HK correctly flagged sync as stale/noisy; `hk sync --exclude .pi --reason ...` was the right way to record that the intended work was limited to `tests/cli_config.rs`.
