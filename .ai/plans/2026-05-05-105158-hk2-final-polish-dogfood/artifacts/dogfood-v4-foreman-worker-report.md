# Foreman HK dogfood worker report

## Change made

- Chosen profile: `rust-mise`, because this is a Rust repo whose repo instructions route validation through `mise` gates; for this narrow slice I used focused native Cargo commands through HK validation.
- Implemented a small CLI/config behavior fix in `src/cli.rs`:
  - extracted the existing `--repo` scope validation into `validate_repo_flag_scope`;
  - applied it to both `run` and `run_main` so the real binary path rejects `--repo` unless paired with `--setup` or `--doctor`;
  - this keeps utility commands like `--config-path` from silently accepting an unsupported `--repo` argument.
- Added focused regression coverage in `tests/cli_config.rs`:
  - existing direct `run` test still proves the library path error;
  - new binary-level test proves `foreman --config-path --repo <path>` exits non-zero, prints nothing to stdout, and reports the existing usage message on stderr.

## Validations run

All validations were run through HK:

1. `hk validate --why 'Focused CLI/config regression for --repo utility guard' --kind test --target . -- cargo test --test cli_config repo_flag -- --nocapture`
   - Result: pass
   - Evidence: `ev_20260505_110452_780476`
2. `hk validate --why 'Rust formatting after CLI guard change' --kind lint --target . -- cargo fmt --check`
   - Result: pass
   - Evidence: `ev_20260505_110516_851434`
3. `hk validate --why 'Full CLI/config integration suite for adjacent behavior' --kind test --target . -- cargo test --test cli_config`
   - Result: pass
   - Evidence: `ev_20260505_110524_675107`

I did not run the full `mise run check` because the task asked for a PR-sized, narrow CLI/config behavior change validated with focused Rust tests; the full adjacent `cli_config` suite plus formatting check covered this slice.

## HK commands tried

Commands are listed in the order I tried them. I did not have any failed HK command mistakes; the only notable non-ready state was HK correctly requiring an external-enough review, which I could not provide as a delegated child worker.

1. `/tmp/hk2-pr-sized-trials-v4/bin/hk --help`
2. `/tmp/hk2-pr-sized-trials-v4/bin/hk status --help`
3. `/tmp/hk2-pr-sized-trials-v4/bin/hk start --help`
4. `/tmp/hk2-pr-sized-trials-v4/bin/hk validate --help`
5. `/tmp/hk2-pr-sized-trials-v4/bin/hk status --target .`
6. `/tmp/hk2-pr-sized-trials-v4/bin/hk brief --target .`
7. `/tmp/hk2-pr-sized-trials-v4/bin/hk profile list --target .`
8. `/tmp/hk2-pr-sized-trials-v4/bin/hk start cli-config-small-behavior --target . --plan 'Pick a narrow CLI/config behavior from existing foreman tests/source, implement a small code+test or test-only improvement, and validate with focused Rust tests. Use rust-mise profile for repo-native validation where needed.' --context 'Task asks to dogfood HK CLI and produce a worker report documenting HK commands, validation, and friction.'`
9. `/tmp/hk2-pr-sized-trials-v4/bin/hk decide --help`
10. `/tmp/hk2-pr-sized-trials-v4/bin/hk plan --help`
11. `/tmp/hk2-pr-sized-trials-v4/bin/hk decide 'Make run_main enforce the same --repo scope guard as run(), then add focused CLI regression tests.' --no-spec-impact --target .`
12. `/tmp/hk2-pr-sized-trials-v4/bin/hk validate --why 'Focused CLI/config regression for --repo utility guard' --kind test --target . -- cargo test --test cli_config repo_flag -- --nocapture`
13. `/tmp/hk2-pr-sized-trials-v4/bin/hk validate --why 'Rust formatting after CLI guard change' --kind lint --target . -- cargo fmt --check`
14. `/tmp/hk2-pr-sized-trials-v4/bin/hk validate --why 'Full CLI/config integration suite for adjacent behavior' --kind test --target . -- cargo test --test cli_config`
15. `/tmp/hk2-pr-sized-trials-v4/bin/hk status --target .`
16. `/tmp/hk2-pr-sized-trials-v4/bin/hk sync --help`
17. `/tmp/hk2-pr-sized-trials-v4/bin/hk sync --target . --exclude .pi --reason 'Pi agent local session state is unrelated to this Foreman CLI/config change.'`
18. `/tmp/hk2-pr-sized-trials-v4/bin/hk status --target .`

## Places I chose not to use HK

- Source exploration used the normal repo tools (`ls`, `find`, `grep`, `read`) because HK is lifecycle-oriented and not a source browser.
- Code edits used the harness `edit` tool directly; HK does not edit source files.
- I used direct `git status --short` and `git diff` inspection to review the working tree and patch details. HK status was useful for lifecycle state but not a replacement for source diff review.
- I did not use `hk review add` because HK explicitly wants an independent/fresh-context review, and this child worker was instructed not to launch subagents or orchestrate review fanout.

## HK workflow friction and helpful guidance

- Helpful: `hk brief` gave a quick repo summary, branch, dirty state, detected instructions/specs, and available profiles without mutating state.
- Helpful: `hk profile list` explicitly said the CLI does not auto-select a profile and gave enough guidance to pick `rust-mise` for this repo.
- Helpful: `hk validate` captured exact command evidence and transcript paths while still running native Cargo commands naturally.
- Helpful: `hk status` surfaced the unrelated `.pi/` local state and suggested the exact `hk sync --exclude .pi --reason ...` shape.
- Friction: the lifecycle cannot reach ready without an external-enough review record. That is reasonable for merge readiness, but it is awkward for a single delegated worker that is explicitly not allowed to fan out a reviewer.
- Friction: validation output for a first Cargo build is long, though the evidence ID/transcript path makes it easy to reference instead of copying logs.

## Final working tree notes

- Intended modified files: `src/cli.rs`, `tests/cli_config.rs`.
- Pre-existing/unrelated local state still present: untracked `.pi/`.
- HK sync checkpoint recorded with `.pi` excluded.
