---
id: plan-implementation
title: Implementation Plan
description: >
  Step-by-step approach for this unit of work.
  Optional — create only when the approach isn't obvious.
---

# Implementation — hk2-readiness-workflow

## Approach

Use the existing plan-artifact workflow to document the HK 2.0 readiness parity
plan. This slice does not add new CLI behavior. It clarifies the product model
and maps the current deterministic scaffold checks to the future ledger-backed
readiness layer.

## Steps

1. Inspect `.mise/tasks/sync-check` and the slice workflow CLI checks.
2. Summarize the actual contract enforced by `plan-check`, `spec-check`,
   `evidence-check`, and `review-check`.
3. Update `docs/harness-kit-2-design.md` with:
   - sync freshness versus readiness;
   - the phase lifecycle;
   - the current artifact to future ledger mapping;
   - planned readiness parity commands.
4. Update `docs/portable-workflow.md` with a clear "which workflow should I
   use?" section.
5. Update `README.md` with the two workflow modes and lifecycle summary.
6. Update `SPEC.md` so the correctness envelope records the future readiness
   parity requirement.
7. Validate docs/tests and record evidence.
8. Run an external-enough review focused on product workflow fit and doc clarity.
