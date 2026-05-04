---
id: plan-decisions
title: Decisions
---

# DECISIONS — hk2-lifecycle-recenter

## What Changed

- Re-centered HK 2.0 product framing on a lifecycle-first CLI that preserves HK
  1.0 handoff-safety guarantees.
- Identified `hk context` as the likely public verb for context-engineering
  material, with `background` demoted to an internal/migration detail.
- Clarified that `hk context` should be agent-guided, not inferred by HK or
  forced as ceremony.
- Decided PR #12 should be reshaped before merge so lifecycle commands exist
  there, instead of landing ledger-first UX as the public 2.0 shape.
- Chose `export` as the public verb for producing shareable handoff files from
  ledger state; `materialize` is implementation/legacy language.
- Decided skipped readiness guarantees should use explicit scary language, e.g.
  dangerous skip/YOLO-style semantics, rather than bland waiver terminology.
- Clarified that profiles and dumb scripts guide `hk validate -- <native command>`
  rather than turning HK into a task runner.
- Clarified that profiles are named validation/workflow guidance objects, while
  `.harness/harness.toml` is optional committed repo adoption/config.
- Added a follow-up to revisit profile vs `.harness/harness.toml` design; likely
  simplification is `.harness` as durable config and profiles as presets/checksets
  or migration compatibility.
- Captured a detailed implementation and dogfood rollout plan in
  `artifacts/lifecycle-implementation-plan.md`.

## Why

- HK 2.0's original goal is a cleaner, simpler HK 1.0, not a different generic
  agent-memory product.
- HK 1.0's strongest value is the lifecycle contract: useful context when it
  prevents rediscovery, explicit plan, spec/decision reflection, validation
  evidence, external-enough review, readiness gate, and handoff artifact.
- If `hk ready` is future work, the current branch is a ledger/capture
  foundation, not the completed HK 2.0 replacement.
- The product should have one obvious promoted path. Lower-level compatibility is
  acceptable only when it is clearly advanced, legacy, or needed for parity.
- HK 2.0 should be dogfooded on real harness-toolkit lifecycle work with
  subagent reviews before public cutover, not validated only through unit tests.
- Final dogfood should include an independent subagent build trial: give agents a
  simple repo and basic product plan, tell them to implement using HK 2.0, and
  evaluate whether the lifecycle works without bespoke hand-holding.

## Where Reflected

- `AGENTS.md`
- `SPEC.md`
- `docs/harness-kit-2-design.md`
- `docs/AGENTS.md`
- `docs/decisions/0009-hk-2-lifecycle-first-cli.md`
- `.ai/plans/2026-05-04-144024-hk2-lifecycle-recenter/artifacts/lifecycle-implementation-plan.md`

## Promotion

- Proposed ADR: `docs/decisions/0009-hk-2-lifecycle-first-cli.md`.
