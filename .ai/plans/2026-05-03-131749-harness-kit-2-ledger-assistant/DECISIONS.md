# Decisions

## What Changed

- Added a ledger-first Harness Kit 2 local assistant command set alongside the current portable workflow commands.
- Added read-only repo briefs, local/external state, work ledgers, typed notes, sync checkpoints, command capture, evidence listing, generated handoffs, and optional local specs.
- Added design docs, ADR, and script-contract prototype documentation for the 2.0 direction.
- Added fixture-heavy unit tests for the new local assistant behavior and script-contract prototype.

## Why

- Local ledgers preserve learning, decisions, gaps, and evidence without recreating committed multi-file plan ceremony.
- Exact command capture gives handoffs trustworthy validation evidence while keeping native shell commands primary.
- Sync checkpoints make agents pause and reconcile work without pretending to score quality.
- Optional local specs let arbitrary repos gain spec-shaped context without forcing committed `SPEC.md` adoption.
- Keeping profiles as guidance avoids heuristic command recommendation behavior.

## Where Reflected

- `src/harness_toolkit/kit/local.py`
- `src/harness_toolkit/kit/cli.py`
- `tests/unit/test_harness_kit_2.py`
- `tests/unit/test_script_contract_prototype.py`
- `docs/harness-kit-lifecycle-design.md`
- `docs/decisions/0008-harness-kit-ledger-first-local-assistant.md`
- `docs/script-contract-prototype.md`
- `docs/portable-workflow.md`
- `SPEC.md`
- `README.md`

## Accepted

- Harness Kit 2.0 is additive in this slice; current `hk plan/status/checks/sync-check` commands remain available during migration.
- Local standardization is allowed; committed harness artifacts require explicit adoption or promotion.
- Work units use `events.jsonl` and `evidence.jsonl` as canonical state. Markdown views are generated/materialized.
- Capture redaction has a built-in baseline now and a pluggable scanner follow-up later.
- Canonical scripts are documented as a prototype direction, not shipped as a scaffold replacement yet.

## Rejected

- Recreating a full multi-file slice bundle as the default 2.0 work artifact.
- Adding `hk run test` or other task-runner commands.
- Adding heuristic profile/check recommendations or confidence scores.
- Making committed `SPEC.md` mandatory for arbitrary existing repos.
- Implementing future orchestration in this slice.
