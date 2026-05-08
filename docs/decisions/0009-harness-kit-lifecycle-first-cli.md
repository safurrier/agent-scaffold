---
id: harness-toolkit-adr-0009
title: ADR 0009 — Harness Kit Lifecycle-First CLI
description: >
  Re-centers Harness Kit on the handoff-safety lifecycle while retaining the
  ledger as an internal implementation detail.
index:
  - id: decision
    keywords: [hk, lifecycle, readiness, validation, review, handoff]
  - id: rollout
    keywords: [hk, ledger, cli, parity, lifecycle]
---

# ADR 0009: Harness Kit Lifecycle-First CLI

**Status**: Proposed
**Date**: 2026-05-04
**Deciders**: Alex Furrier
**Generated from**: Harness Kit product-direction review
**Plan**: lifecycle recenter planning artifacts
**Amends**: `docs/decisions/0008-harness-kit-ledger-first-local-assistant.md`

---

## Context

ADR 0008 defined Harness Kit as a ledger-first local repo assistant. That produced a
useful substrate: read-only repo briefs, local work ledgers, typed notes,
command capture, sync checkpoints, generated handoffs, and optional local specs.

The product review identified a drift in framing. The original goal for Harness Kit
was not to create a different generic agent-memory product. The goal was a
cleaner, simpler handoff lifecycle.

The core value was not the exact `.ai/plans/` directory shape. It was the
handoff-safety lifecycle:

```text
plan → spec/decision reflection → validation evidence → external-enough review → readiness gate → handoff artifact
```

If Harness Kit lacks that lifecycle or leaves readiness as future work, then it is only a ledger/capture substrate, not the product shape.

## Decision

Re-center Harness Kit around a lifecycle-first CLI that preserves the handoff
contract while using the ledger as the internal storage model.

The target public workflow should be close to:

```bash
hk start <slug> --plan "..."
hk context "..."  # optional, when it prevents rediscovery
hk status
hk decide "..." --spec-impact none
hk validate --why "unit tests cover the new branch" -- uv run pytest ...
hk review prompt
hk review add --backend subagent --reviewer reviewer-fresh-context --rubric core-quality --summary "..."
hk sync --exclude .pi --reason "Only local agent state changed"
hk ready
hk handoff
```

`hk plan "..."` remains the refinement command when an already-active work item
needs an updated lifecycle plan. Portable plan-artifact creation is no longer
part of `hk`; scaffolded repos use `mise run plan` from the slice-workflow task
contract.

The ledger remains useful, but it should be an implementation detail behind
clear lifecycle verbs. Users should not have to think in terms of generic note
kinds for the common path. `hk context` is intentionally a product verb: HK is
capturing context-engineering material for the next human or agent, including
stable framing, constraints, relevant files, assumptions, and discovered repo
facts.

`hk context` should be agent-guided, not magically inferred. The expected flow is
that human and agent discuss/design outside HK, then the agent distills only the
useful durable context into HK. Tiny obvious changes may need no context record;
HK should not force filler just to satisfy a template.

### Preserve the handoff guarantees

Before Harness Kit replaces the plan-artifact workflow, it must preserve these
guarantees:

1. Important context is captured when it prevents rediscovery or clarifies repo
   facts, constraints, assumptions, relevant files, or prior discovery.
2. There is an explicit plan.
3. There is explicit spec/decision reflection.
4. There is validation evidence with rationale.
5. There is external-enough review evidence, or an explicit `hk dangerously-skip review --label ... --reason ... --mitigation ...` record.
6. There is a binary readiness gate.
7. There is a rendered handoff artifact.

### Keep the simplification

Preserving the lifecycle does not require preserving the plan-file ceremony. Harness Kit
should avoid:

- mandatory seven-file plan directories for every slice;
- hand-edited validation manifests;
- confusing `sync-check` naming that mixes freshness and readiness;
- committed scaffold files for arbitrary existing repos;
- task-runner UX such as `hk run test`.

### Separate freshness from readiness

Keep the split:

- `hk sync --check` answers whether work changed since the last reconciliation
  checkpoint.
- `hk ready` answers whether explicit lifecycle declarations are sufficient for
  handoff.

Readiness should remain binary and explanation-oriented. It should report missing
or inconsistent declarations, not assign scores or infer quality.

## Consequences

### Positive

- Aligns Harness Kit with the product goal: a cleaner lifecycle, not a separate
  product.
- Preserves the strongest part of the scaffold workflow: auditable handoff
  readiness.
- Keeps the ledger implementation work useful without exposing it as the main
  user mental model.
- Produces a smaller, more memorable CLI surface.

### Negative / Trade-offs

- Existing Harness Kit note commands may become lower-level or advanced
  aliases rather than equally promoted workflows.
- The current docs that describe Harness Kit as primarily a local assistant need to be
  revised.
- Readiness parity becomes a launch blocker for promoting the ledger workflow.
- Additional schema is needed for validation rationale and review records.
- PR #12 should be reshaped before merge so lifecycle commands exist there,
  instead of landing the ledger-first UX as the public product shape.

## Rollout sketch

1. Keep the current ledger state and command-capture foundation.
2. Add lifecycle aliases or first-class commands:
   - `hk start` over `hk work start`.
   - `hk context` for context-engineering records.
   - `hk start --plan` as the common path for initial plan records.
   - `hk plan` as the refinement path for active-work plan records.
   - `hk decide` for decision/spec reflection records.
   - `hk validate --why ... -- <command>` over capture evidence.
   - `hk review add` for external-enough review records.
   - `hk ready` for lifecycle readiness.
3. Make `hk handoff` render lifecycle-oriented sections, not generic note dumps.
4. Once `hk ready` reaches parity for existing-repo Harness Kit lifecycle work, remove
   portable plan-artifact compatibility from `hk` rather than keeping a second public
   workflow.
5. Keep scaffold/task-contract plan packages on `mise run plan` and `mise run
   sync-check`, backed by the separate slice-workflow CLI.

## Alternatives considered

### Continue with generic typed notes as the primary UX

Rejected as the primary lifecycle shape. Typed notes are flexible, but they make users
assemble the lifecycle themselves and obscure the original product promise.

### Keep `.ai/plans/` as canonical forever

Rejected because Harness Kit should be simpler than the plan-file ceremony. Plan
directories may remain as an export/materialized compatibility format.

### Build task-runner commands

Rejected. HK can capture native commands but should not hide project validation
behind `hk run`.
