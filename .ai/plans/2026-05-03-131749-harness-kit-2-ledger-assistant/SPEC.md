# Slice SPEC

## Goal

Implement the first complete pass of Harness Kit 2.0 as a ledger-first local
assistant while preserving the current CLI during migration.

## Scope

This slice adds:

- canonical 2.0 design docs and ADR;
- read-only `hk brief`;
- ignored/external 2.0 local state via `hk init`;
- ledger-backed work units via `hk work`;
- typed notes via `hk note`;
- sync checkpoints via `hk sync`;
- command evidence via `hk capture`;
- evidence listing;
- conservative handoff generation;
- optional local spec support;
- script-contract prototype docs/tests;
- docs and root spec updates.

## Non-Goals

- Delete current `hk plan/status/checks/sync-check` commands.
- Replace scaffold's mise task contract in generated repos.
- Implement Web/TypeScript scaffold.
- Implement future orchestration.
- Add heuristic profile or command recommendation logic.

## Acceptance Criteria

- New commands have fixture tests.
- `hk brief` does not mutate target repos and does not emit recommendation or confidence fields.
- Local state is ignored through `.git/info/exclude`.
- External state creates no checkout files.
- Work ledger notes and materialized views are deterministic.
- Sync is binary/freshness-based and emits no scores.
- Capture preserves exit code and redacts seeded fake secrets.
- Handoff does not overclaim validation.
- Local specs stay uncommitted and promote by dry-run.
- `mise run check` passes.
