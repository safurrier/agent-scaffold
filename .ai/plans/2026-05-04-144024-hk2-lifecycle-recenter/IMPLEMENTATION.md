---
id: plan-implementation
title: Implementation Notes
---

# IMPLEMENTATION — hk2-lifecycle-recenter

## Current slice

This slice captures the product-direction correction and implementation plan. It
also updates durable docs. It does not implement the new CLI yet.

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

- `hk start <slug>`
- `hk status`
- `hk context "..."`
- `hk plan "..."` / `hk plan --from-file`
- `hk decide "..." --spec-impact ...` / `--no-spec-impact`
- Lifecycle-oriented handoff rendering.

### Slice 2 — Validation rationale

- `hk validate --why "..." -- <command>` as primary validation/evidence path.
- Preserve `hk capture` as lower-level command evidence.

### Slice 3 — Review records

- `hk review add` with backend, reviewer, rubric, summary, disposition.
- Accepted external-enough sources: AI subagent review, manual human review,
  GitHub PR review.

### Slice 4 — Ready gate

- `hk ready` strict by default with explicit waivers/gaps.
- Checks plan, decision/spec reflection, validation rationale, external review,
  sync freshness, and handoff renderability.
- Does not fail by default solely because no context exists; context is
  agent-guided and informational unless a future strict profile says otherwise.

### Slice 5 — Export/materialize and deprecation plan

- Decide whether materialization becomes `hk export`.
- Optionally export legacy plan-dir/handoff packages from ledger state.
- Deprecate/remove old `hk plan/checks/sync-check` only after readiness parity.
