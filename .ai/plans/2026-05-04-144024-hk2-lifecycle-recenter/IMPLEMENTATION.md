---
id: plan-implementation
title: Implementation Notes
---

# IMPLEMENTATION — hk2-lifecycle-recenter

## Current slice

This slice captures the product-direction correction and implementation plan,
then reshapes PR #12 with the first lifecycle CLI implementation.

Changed/added docs:

- `AGENTS.md` — records the product correction as repo-specific tribal knowledge.
- `docs/decisions/0009-hk-2-lifecycle-first-cli.md` — ADR for lifecycle-first HK
  2.0.
- `docs/AGENTS.md` — routes the new ADR.
- `docs/harness-kit-2-design.md` — amends thesis and CLI target.
- `SPEC.md` — adds lifecycle-first HK 2.0 invariant and target interface.
- `artifacts/product-postmortem.md` — captures the product correction.
- `artifacts/lifecycle-implementation-plan.md` — task-by-task implementation
  plan with tests, validation, and open questions.

## Implementation path summary

Full details are in `artifacts/lifecycle-implementation-plan.md`.

### Slice 0 — Reframe current PR before merge

- Update docs/ADR/SPEC to lifecycle-first language.
- Keep ledger/capture work as foundation.
- Reshape PR #12 before merge so the lifecycle commands exist there.

### Slice 1 — Start/status and lifecycle record commands

Implemented in this branch:

- `hk start <slug>`
- lifecycle-oriented `hk status`
- `hk context "..."`
- `hk plan "..."` / `hk plan --from-file`
- `hk decide "..." --spec-impact ...` / `--no-spec-impact`
- lifecycle-oriented handoff rendering.

### Slice 2 — Validation rationale

Implemented in this branch:

- `hk validate --why "..." -- <command>` as primary validation/evidence path.
- `why` rationale stored in evidence records and rendered in handoff/evidence
  output.
- `hk capture` preserved as lower-level command evidence.

### Slice 3 — Review records

Implemented in this branch:

- `hk review add` with backend, reviewer, rubric, summary, disposition.
- Review records render in handoff and feed readiness.

### Slice 4 — Ready gate

Implemented initial strict readiness gate:

- `hk ready` and `hk ready --json`.
- Checks plan, decision/spec reflection, validation rationale, external review,
  sync freshness, and handoff renderability.
- Does not fail by default solely because no context exists; context is
  agent-guided and informational unless a future strict profile says otherwise.
- `hk dangerously-skip review|validation --reason ...` records explicit dangerous
  skips. The exact final spelling can still be refined.

### Slice 5 — Export/materialize and deprecation plan

- Decide whether materialization becomes `hk export`.
- Optionally export legacy plan-dir/handoff packages from ledger state.
- Deprecate/remove old `hk plan/checks/sync-check` only after readiness parity.
