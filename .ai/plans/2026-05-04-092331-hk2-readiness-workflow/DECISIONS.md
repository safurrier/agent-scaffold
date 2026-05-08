---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — hk2-readiness-workflow

## What Changed

- Documented that HK 2.0 `hk sync --check` is a freshness check, while current `mise run sync-check` is a handoff-readiness gate.
- Documented the intended research → plan → implement → validate → review → handoff lifecycle.
- Added the readiness parity target: task events, validation rationale, review records, `hk ready --check`, and plan-directory materialization from ledger state.
- Clarified the two current `hk` workflows: ledger-first local assistant and plan-artifact workflow.

## Why

- The first HK 2.0 implementation risks appearing ready to replace the old plan-artifact workflow even though it does not yet enforce the same readiness contract.
- Agents need clearer onboarding so they know when to use local ledgers versus durable plan artifacts.
- Validation evidence should remain agent-declared and reviewable rather than being judged by heuristic scoring.
- Reviews should become structured enough to support multiple future review styles and parallel rubric-specific reviews.

## Where Reflected

- `docs/harness-kit-lifecycle-design.md`
- `docs/portable-workflow.md`
- `README.md`
- `SPEC.md`
- `.ai/plans/2026-05-04-092331-hk2-readiness-workflow/SPEC.md`
- `.ai/plans/2026-05-04-092331-hk2-readiness-workflow/IMPLEMENTATION.md`

## Promotion

- Docs-only clarification. No ADR required because the earlier ADR still owns the ledger-first assistant direction; this slice refines migration/readiness parity documentation.
