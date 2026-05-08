---
id: plan-decisions
title: Decision Log
description: >
  Decisions made while implementing this unit of work.
---

# DECISIONS — hk-summary-skip-mitigation

## What Changed

- Added `hk summary` as the human-readable readiness digest.
- Required dangerous skips to carry `label`, `reason`, and `mitigation`.
- Updated docs/help to position HK as a readiness ledger for serious agent-driven changes.
- Documented progressive planning through existing repeated `hk plan` records.

## Why

- Dogfood feedback showed the core value is readiness evidence, not task execution.
- Users need a concise PR/review-oriented summary distinct from `hk status` and the longer `hk handoff`.
- Dangerous skips are valuable only if they explain both the gap and how the risk is mitigated.
- Adding `hk quick` or workflow tiers would create a second lifecycle and risk teaching agents to downgrade the workflow on their own.

## Where Reflected

- `src/harness_toolkit/kit/cli.py`
- `src/harness_toolkit/kit/app/lifecycle.py`
- `src/harness_toolkit/kit/local.py`
- `src/harness_toolkit/kit/readiness/policy.py`
- `src/harness_toolkit/kit/rendering/handoff.py`
- `src/harness_toolkit/kit/ledger/store.py`
- `README.md`
- `docs/agent-adoption.md`
- `docs/portable-workflow.md`
- `docs/harness-kit-lifecycle-design.md`
- `tests/unit/test_harness_kit_2.py`
- `tests/unit/test_hk2_lifecycle_parity.py`

## Promotion

- No ADR needed; these are refinements within the existing lifecycle-first HK direction.
