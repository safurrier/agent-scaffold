---
id: harness-toolkit-adr-0012
title: ADR 0012 — Lifecycle-Neutral Active HK Exports
description: >
  Treats the active `.ai/hk/<work-id>/` handoff export as a generated derived
  artifact for readiness, sync, validation, and review freshness while preserving
  strict export integrity checks.
index:
  - id: decision
    keywords: [hk, export, readiness, sync, freshness]
  - id: guardrails
    keywords: [.ai/hk, handoff-dir, sync-check, integrity]
---

# ADR 0012: Lifecycle-Neutral Active HK Exports

**Status**: Accepted  
**Date**: 2026-05-15  
**Deciders**: Alex Furrier  
**Generated from**: pr  
**Origin**: Foreman/HK export-status dogfood  
**Amends**: `docs/decisions/0010-compact-hk-export-packages.md`, `docs/decisions/0011-path-aware-review-freshness.md`

---

## Context

HK handoff-dir exports are generated projections of HK ledger state. They are
committed when durable review context helps, but the canonical lifecycle state is
still the HK ledger.

Foreman/HK dogfood exposed a finalization loop: after validation, review, and
sync, running `hk export --format handoff-dir` wrote `.ai/hk/<work-id>/...` files
that could make readiness or sync freshness look stale. That made the generated
handoff package perturb the lifecycle state it was supposed to represent.

The expected invariant is:

```bash
hk ready --target . --json
hk export --format handoff-dir --target .
hk export --format handoff-dir --target . --check --json
hk ready --target . --json
```

If no real work state changed, the export check should be fresh and readiness
should remain ready.

## Decision

Treat the active handoff export directory, `.ai/hk/<active-work-id>/`, as a
generated derived artifact for lifecycle freshness.

The active export directory is excluded from:

- sync diff hashes and sync freshness checks;
- validation/review freshness diff hashes;
- changed-path lists used for readiness/profile review coverage;
- profile check/review matching driven by current changed paths.

Export integrity remains strict and separate. `hk export --format handoff-dir
--check` and `mise run sync-check` still validate the generated package's
metadata, hashes, expected file set, symlink safety, and copied artifact
integrity.

Only the active work's export directory receives this lifecycle-neutral treatment.
Other `.ai/hk/<work-id>/` directories remain normal repository changes.

## Consequences

### Positive

- `ready + exported` becomes a stable final handoff state.
- Foreman can stay read-only and show/copy export commands without trying to
  repair HK state.
- Generated export refreshes do not require another validation, review, or sync
  solely because HK rewrote its own projection.
- Export package tampering is still caught by export/sync-check integrity checks.

### Negative / Trade-offs

- Readiness no longer treats active export package changes as work-content
  changes. This is intentional, but it makes export integrity checks mandatory
  when committed exports are part of handoff.
- Operators must understand the difference between lifecycle freshness and export
  package integrity.
- Existing sync checkpoints recorded before this rule may need one explicit
  `hk sync` refresh if the active export package changes after upgrade. Older
  checkpoints did not store a source-only hash, so HK cannot always prove that
  only generated active-export bytes changed.

### Guardrails

- Do not ignore all `.ai/hk/**`; only `.ai/hk/<active-work-id>/` is
  lifecycle-neutral.
- Do not read generated export Markdown back as canonical state.
- Do not weaken `hk export --format handoff-dir --check` or `mise run sync-check`.
- Continue validating path traversal, symlink, file-hash, and copied-artifact
  invariants for committed exports.

## Alternatives considered

### Keep active exports as normal changed files

Rejected. It is conservative, but it creates a self-referential completion loop:
HK-generated projection files make HK freshness stale.

### Ignore all `.ai/hk/**`

Rejected. Historical or unrelated HK exports should remain visible as normal
repository changes unless they are the active work's generated projection.

### Move export packages outside the repository

Rejected as the only solution. Foreman and review flows sometimes need committed,
shareable handoff packages. External previews remain useful, but committed exports
must be stable when intentionally generated.
