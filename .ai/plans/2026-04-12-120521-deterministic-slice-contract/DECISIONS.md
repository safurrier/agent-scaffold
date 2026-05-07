---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — deterministic-slice-contract

## What Changed

- Expanded the task contract with `plan-check`, `spec-check`, `evidence-check`,
  `review-check`, and `sync-check`.
- Enriched plan templates with `REVIEW.md`, `DECISIONS.md`, and
  `artifacts/manifest.yaml`.
- Switched generated docs to an intent-structured layout with
  `docs/explanation/`, `docs/reference/`, and review rubrics.
- Added vendored workflow skills for `slice-planner`, `slice-implementer`, and
  `slice-reviewer`.
- Hardened the validator helpers so placeholder TODO checkboxes, fake fenced
  validation blocks, and artifact paths escaping the active plan directory do
  not satisfy handoff checks.

## Why

- The old scaffold left too much of plan/spec/evidence/review completion to
  soft prompting, which let slices end half done.
- A repo-enforced handoff gate is more generic and durable than a
  product-specific harness template.

## Where Reflected

- `docs/decisions/0003-deterministic-slice-contract.md`
- `docs/task-<REDACTED_TOKEN>.md`
- `.mise/tasks/evidence-check`
- `scripts/plan_contract.py`
- `tests/unit/test_plan_contract.py`
- `templates/.ai/plans/AGENTS.md`
- `templates/docs/explanation/architecture.md.tmpl`
- `templates/docs/reference/review-rubrics/core-quality.md.tmpl`

## Promotion

- Promoted to ADR `docs/decisions/0003-deterministic-slice-contract.md`.
