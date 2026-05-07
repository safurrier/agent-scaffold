---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — followup-contract-stack-rubric

## What Changed

- Moved slice workflow implementation into the `slice-workflow` skill-local CLI.
- Replaced repo-local script imports in `.mise/tasks/*` with thin uv wrapper
  scripts.
- Removed obsolete `scripts/plan_contract.py`, `scripts/plan_contract_core/`,
  and `scripts/slice_workflow.py`.
- Added a stack acceptance rubric for future stack additions.

## Why

- Issue #6 identified plan-contract checks as too much logic in one helper file.
- User review identified the interim `scripts/` module split as still too
  scaffold-local; the capability belongs with the workflow skill.
- Issue #7 identified an implicit stack quality bar that should be explicit
  before the next stack lands.

## Where Reflected

- `templates/.agent/skills/slice-workflow/cli`
- `.mise/tasks/plan`
- `.mise/tasks/plan-check`
- `.mise/tasks/spec-check`
- `.mise/tasks/evidence-check`
- `.mise/tasks/review-check`
- `.mise/tasks/sync-check`
- `.mise/tasks/slice-plan`
- `.mise/tasks/slice-implement`
- `.mise/tasks/slice-review`
- `.mise/tasks/slice-status`
- `docs/task-<REDACTED_TOKEN>.md`
- `docs/stacks/acceptance-rubric.md`
- `docs/development.md`
- `docs/stacks/index.md`
- `docs/decisions/0006-followup-contract-stack-rubric.md`

## Promotion

- Promoted to `docs/decisions/0006-followup-contract-stack-rubric.md`.
