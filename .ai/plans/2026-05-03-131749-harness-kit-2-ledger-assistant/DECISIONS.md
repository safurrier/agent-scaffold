# Decisions

## Accepted

- Harness Kit 2.0 is implemented as additive 2.0 commands first, not by immediately deleting current `hk plan/status/checks/sync-check` commands.
- Local standardization is allowed. The dangerous boundary is accidental committed repo ceremony, so 2.0 local state writes under ignored `.harness-local/harness-kit/` or external state.
- Work units use append-only `events.jsonl` and `evidence.jsonl` as canonical state. Markdown learning/decision/gap/handoff views are generated/materialized.
- Learning, decisions, gaps, context, and spec impact are captured as typed note events.
- `hk sync` is a checkpoint/freshness bit, not a semantic quality validator or readiness score.
- Profiles remain guidance; `hk brief` reports facts and does not mine/recommend validation commands.
- `hk capture` records exact native command evidence and preserves the wrapped command's exit code.
- Capture gets a built-in redaction baseline plus raw/no-log controls; deeper scanner integration remains follow-up hardening.
- Optional local specs can exist in harness state and be promoted by dry-run before any committed write.
- Canonical scripts are captured as a prototype direction, not a full scaffold migration in this slice.

## Rejected

- Recreating a full multi-file slice bundle as the default 2.0 work artifact.
- Adding `hk run test` or other task-runner commands.
- Adding heuristic profile/check recommendations or confidence scores.
- Making committed `SPEC.md` mandatory for arbitrary existing repos.
- Implementing future orchestration in this slice.
