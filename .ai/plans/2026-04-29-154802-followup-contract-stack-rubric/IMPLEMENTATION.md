---
id: plan-implementation
title: Implementation Plan
description: >
  Step-by-step approach for this unit of work.
  Optional — create only when the approach isn't obvious.
---

# Implementation — followup-contract-stack-rubric

## Approach

Handle both issues in one narrow branch because they are follow-ups to the same
merged contract work. The implementation now has three parts:

- Move the plan-contract and slice prompt implementation into the
  `slice-workflow` skill-local uv CLI.
- Replace repo-local script imports in `.mise/tasks/*` with thin wrappers around
  the skill CLI while keeping task names stable.
- Add a stack acceptance rubric under `docs/stacks/`, wire it into MkDocs, and
  add deterministic checks that the rubric and reviewer checklist exist.

## Steps

1. Add failing tests that require a uv-backed CLI at
   `templates/.agent/skills/slice-workflow/cli`.
2. Move plan creation, prompt rendering, and sync-contract checks into
   `slice_workflow_cli`.
3. Replace the plan/check/slice task scripts with thin wrappers that invoke
   `uv run --project <skill>/cli slice-workflow`.
4. Delete the obsolete `scripts/plan_contract.py`, `scripts/plan_contract_core/`,
   and `scripts/slice_workflow.py` code paths.
5. Add `docs/stacks/acceptance-rubric.md` and link it from stack overview,
   development docs, and MkDocs navigation.
6. Add or update contract tests to assert the rubric contains the future-stack
   checklist and the smoke matrix requirements.
7. Add an ADR explaining the skill-local CLI boundary and stack rubric.
8. Validate with focused tests, generated-project smoke, `mise run check`, and
   PR-mode sync-check.
