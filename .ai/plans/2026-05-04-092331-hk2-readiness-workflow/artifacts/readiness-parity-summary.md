# HK 2.0 Readiness Parity Summary

## Purpose

Summarize how the current scaffold `mise run sync-check` contract maps to the
HK 2.0 ledger-first workflow direction.

## Current sync-check contract

`mise run sync-check` delegates to the slice workflow CLI and aggregates four
checks:

1. `plan-check`
   - required plan files exist;
   - `META.yaml` contains required fields;
   - active plan branch matches git branch;
   - `TODO.md` contains meaningful checklist items;
   - active/in-progress work records learning notes.
2. `spec-check`
   - `DECISIONS.md` contains meaningful `What Changed` and `Why` sections;
   - docs/contract changes list durable reflected paths;
   - ADR/ledger decision records reference the active plan when configured.
3. `evidence-check`
   - `VALIDATION.md` contains real commands or captured verification output;
   - artifact manifest entries have type/path;
   - artifact paths are inside the plan, exist, are not gitignored, and are
     tracked/staged;
   - required evidence types are present.
4. `review-check`
   - `REVIEW.md` contains external-enough review context;
   - backend, reviewer, rubrics, findings, and disposition are meaningful;
   - required rubrics from `META.yaml` are covered.

## HK 2.0 target

HK 2.0 should keep the ledger as the canonical source of truth while preserving
those readiness guarantees through explicit declarations:

- research/context as learning/context events;
- plan as task events;
- decisions/spec impacts as structured decision and spec-impact events;
- validation as captured command evidence plus rationale;
- review as backend/reviewer/rubric/finding/disposition events;
- handoff readiness as future `hk ready --check`;
- old-style plan directories as generated/materialized views when needed.

## Non-goal

HK should not infer semantic quality, choose validation commands, score
readiness, or auto-select profiles. Agents choose and explain; HK records,
checks presence/consistency, and renders evidence for review.
