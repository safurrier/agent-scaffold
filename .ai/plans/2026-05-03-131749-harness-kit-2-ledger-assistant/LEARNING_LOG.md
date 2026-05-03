# Learning Log

## Product/design

- Local generated state is acceptable when it is ignored or external; the key product boundary is explicit promotion/commit.
- Ledger-first work units preserve learning/decisions/gaps without forcing a multi-file ceremony.
- Sync works best as a checkpoint/freshness bit that makes the agent pause, not as a semantic quality validator.
- Profile list/show/create guidance is preferable to source-mined command candidates because it avoids drifting back into heuristic recommendation behavior.

## Implementation

- Cyclopts can accept `tuple[str, ...]` for `hk capture -- <command...>` style command arguments.
- `hk capture` must print normal command output live and then return the wrapped command's exit code, so failure evidence still behaves like a failed shell command.
- `mise run check` catches formatting and ty issues that focused pytest does not; it should remain the local gate during this migration.

## Follow-up

- Redaction should be hardened with a pluggable scanner after evaluating `scrubadub`, `detect-secrets`, `gitleaks`, and `trufflehog`.
- Script-contract migration needs generated-repo prototypes before replacing the current mise-first scaffold contract.
