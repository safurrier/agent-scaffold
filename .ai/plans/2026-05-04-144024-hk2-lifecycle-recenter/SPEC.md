---
id: plan-spec
title: Scoped Spec
---

# SPEC — hk2-lifecycle-recenter

## Problem

HK 2.0 drifted toward a generic ledger-first local assistant. That foundation is
useful, but the original product goal was a cleaner, simpler HK 1.0. HK 1.0's
core value was handoff safety, not the specific `.ai/plans/` file layout.

## Desired product shape

HK 2.0 should expose a lifecycle-first CLI:

```bash
hk start <slug>
hk context "..."
hk plan "..."
hk decide "..."
hk validate --why "unit tests cover the new branch" -- uv run pytest ...
hk review add --summary "..."
hk ready
hk handoff
```

The ledger should remain the internal storage substrate. The public mental model
should be the handoff lifecycle. `hk context` is part of that lifecycle because
HK is doing context engineering: capturing stable framing, constraints, relevant
files, assumptions, and discovered repo facts for the next human or agent.

## Invariants

- HK 2.0 must preserve the HK 1.0 handoff-safety spine: context when needed,
  plan, spec/decision reflection, validation evidence, external-enough review,
  readiness gate, and handoff artifact.
- HK must stay shell-first: native commands are captured, not hidden behind
  `hk run`.
- `hk sync --check` remains freshness-only.
- `hk ready` is readiness-only and reports missing/inconsistent explicit
  declarations without heuristic scores.
- Existing plan-artifact workflow remains supported until readiness parity lands.

## Acceptance for this planning slice

- Product correction is captured in an ADR.
- Repo context tells future agents not to treat generic note-ledger UX as the HK
  2.0 goal.
- Design/spec docs name the lifecycle-first command shape and launch blockers.
- A follow-up implementation path is clear enough to plan code slices.
