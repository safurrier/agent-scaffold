# HK2 agent ergonomics design questionnaire summary

Date: 2026-05-05

## Accepted scope

The next implementation slice should include:

- `hk start <slug> --plan '...'`.
- Optional `hk start <slug> --context '...'`.
- Root `hk plan` should be lifecycle-only; legacy plan artifact creation should remain under `hk legacy plan`.
- `hk status` should become a preflight / next-action coach.
- `hk dangerously-skip sync --reason '...'` should provide an explicit escape hatch for known sync freshness issues.

Structured spec/docs references are deferred. Keep the existing `--spec-impact` / `--no-spec-impact` decision surface for this slice.

## Behavior decisions

### `hk start --plan`

Create the work record and immediately append one lifecycle plan event. Do not only print a follow-up command.

### `hk start --context`

Optional seed context. Record only when provided. Examples should steer usage toward constraints, relevant files, and repo facts that prevent rediscovery.

### `hk status`

Coach on:

- active work slug and target;
- missing plan before implementation;
- optional context guidance when no context exists;
- missing decision/spec-impact reflection after changes;
- missing passing validation evidence;
- missing independent review or dangerous review skip;
- stale sync checkpoint and agent-local state hints.

### `hk dangerously-skip sync`

Require `--reason`, record a dangerous skip event, allow readiness to pass, and render the skip prominently in handoff.

## Rollout test

After implementation, run a targeted PR-sized dogfood rerun with three workers in temporary repos. Focus the test on whether agents use:

- `hk start --plan`;
- `hk status` for preflight/next-action guidance;
- `hk dangerously-skip sync` for `.pi`/agent-local freshness issues.

## Open clarifications captured during questionnaire

### Slug guidance

The user wants clearer guidance on what a slug is and how it relates to chronological ordering. Recommendation: keep user-provided slugs short and human-readable, and continue storing chronological order in HK-generated timestamps / work IDs rather than making users encode dates manually.

### `hk plan` vs `hk start --plan`

`hk start --plan` is a convenience that starts work and records the first lifecycle plan event in one command. Root `hk plan '...'` should remain the command for adding/replacing a lifecycle plan record after work is already active. Legacy plan artifact creation should only be `hk legacy plan <slug>`.
