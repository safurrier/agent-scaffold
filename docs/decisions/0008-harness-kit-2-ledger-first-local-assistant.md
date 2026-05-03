---
id: harness-toolkit-adr-0008
title: ADR 0008 — Harness Kit 2.0 Ledger-First Local Assistant
description: >
  Defines Harness Kit 2.0 as a shell-first, ledger-backed local assistant with
  evidence capture, sync checkpoints, optional local specs, and explicit
  promotion boundaries.
index:
  - id: decision
    keywords: [hk, ledger, local-assistant, evidence, sync, spec]
  - id: consequences
    keywords: [migration, breaking, profiles, scaffold, orchestration]
---

# ADR 0008: Harness Kit 2.0 Ledger-First Local Assistant

**Status**: Accepted
**Date**: 2026-05-03
**Deciders**: Alex Furrier
**Generated from**: Harness Kit 2.0 product/design discussion
**Plan**: `.ai/plans/2026-05-03-131749-harness-kit-2-ledger-assistant/`

---

## Context

Harness Toolkit currently has two related surfaces:

1. `hk` / `harness-kit`, a portable workflow CLI for existing repos.
2. `harness-scaffold`, an opinionated starter template with a stable task and
   slice-handoff contract.

The current portable workflow proved useful, but its primary concepts are still
profiles, plans, checks, and sync-check. That can pull agents toward a tool-shaped
workflow instead of normal shell work.

The desired 2.0 direction is:

> Do not make agents use a worse shell. Give them a better repo map, better
> validation evidence, and better handoff artifacts.

The design discussion refined that further:

- local state may be rich as long as it is not accidentally committed;
- learning, decisions, gaps, and handoff are valuable, but should not recreate
  mandatory multi-file slice ceremony;
- `sync` should make agents stop and reconcile, not pretend to score quality;
- specs are useful even in arbitrary repos, but should be local/external until
  explicitly promoted;
- profiles should remain guidance, not heuristic auto-detection;
- future orchestration should be designed for, not shipped in 2.0.

## Decision

Define Harness Kit 2.0 as a shell-first local repo assistant.

### Ledger-first work units

The canonical work state is an append-only ledger:

```text
<harness-state>/work/<timestamp>-<slug>/
  events.jsonl
  evidence.jsonl
  artifacts/
  views/
```

Markdown views such as learning logs, decisions, gaps, and handoff are generated
or materialized from the ledger. They are not the source of truth by default.

### Typed notes

Learning, decisions, gaps, context, and spec impact are captured as typed events:

```bash
hk note --kind learning "..."
hk note --kind decision "..."
hk note --kind gap "..."
hk note --kind spec-impact "..."
```

### Command evidence

`hk capture -- <command>` records exact command evidence while keeping native
commands primary. It must preserve command identity, cwd, target, git state,
timestamps, duration, exit code, transcripts, and redaction metadata.

`hk` must not add task-runner UX such as `hk run test`.

### Sync checkpoints

`hk sync` records a checkpoint for the current work snapshot and prints a short
reconciliation prompt. `hk sync --check` is binary: synced or needs sync.

Sync is not a readiness score and not a semantic quality validator.

### Optional local specs

Existing repos may have local/external spec drafts without committing `SPEC.md`.
Committed `SPEC.md` wins when present. Spec promotion is explicit and should
support dry-run before writing.

### Profiles remain guidance

Keep profile listing, showing, and creation. Do not add heuristic command mining,
confidence scores, or silent profile selection. Agents use repo docs, profile
guidance, and the profile-authoring skill to choose or propose profiles.

### Explicit committed boundary

Default `hk` usage in existing repos must not commit harness artifacts. Rich local
state is acceptable; committed config requires explicit adoption, using
`.harness/` as the future config root.

## Consequences

### Positive

- Keeps agents close to native repo tooling.
- Preserves valuable work history without mandatory Markdown ceremony.
- Makes validation evidence more trustworthy through command capture.
- Gives `sync` a clear, non-theatrical purpose.
- Allows specs to compound locally before repo adoption.
- Avoids profile auto-selection and readiness scoring pitfalls.
- Creates state contracts future orchestration can consume later.

### Negative / Trade-offs

- This is a breaking product migration from the current `hk plan/status/checks`
  model.
- The event/evidence ledger adds new schemas that must be versioned and tested.
- Capture redaction is non-trivial and needs a pluggable design.
- Markdown views become generated artifacts, so users who prefer direct editing
  need a materialization workflow.
- Scaffold task-contract migration is deferred rather than solved immediately.

### Migration impact

Implementation should be staged. Compatibility does not need to be preserved as a
public product promise, but each phase should have fixture/parity-style tests
before replacing current behavior.

## Alternatives Considered

### Keep current profile/plan/sync-check model

Rejected as the 2.0 target because it keeps plan ceremony too central and does
not provide exact command evidence.

### Full Markdown work bundle by default

Rejected as the default because it recreates much of the current slice ceremony.
Markdown views remain available as generated/materialized outputs.

### Delete sync entirely

Rejected because the checkpoint motion is useful. The semantics are changed from
handoff quality validation to freshness/reconciliation.

### Automatic profile/check detection

Rejected because it drifts toward heuristic command recommendations. `hk brief`
may report facts, but agents choose validation commands using repo instructions
and profile guidance.

### Require committed SPEC.md everywhere

Rejected because non-invasive existing-repo adoption is a core goal. Local specs
provide a path to spec-shaped context without forcing commits.

### Build future orchestration now

Rejected as scope creep. 2.0 should make orchestration possible later through
clean state/evidence contracts, not ship a daemon or issue-tracker control plane.
