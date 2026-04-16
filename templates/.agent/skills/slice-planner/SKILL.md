---
name: slice-planner
description: >
  Shape the active slice before coding. Updates the plan, declares evidence and
  review expectations, and records contract/decision intent up front.
allowed-tools: Read, Edit, Glob, Grep, Bash
---

Use this skill when starting a new slice or when the scope changes enough that
the active plan no longer matches reality.

## Workflow

1. Create or locate the active plan
2. Update `META.yaml`:
   - `status`
   - `contract_change`
   - `decision_record`
   - `review_rubrics`
   - `evidence_required`
3. Tighten `TODO.md` into real slice steps
4. Seed `DECISIONS.md` with the intended change summary and likely durable docs
5. Add `SPEC.md` / `IMPLEMENTATION.md` if the slice is non-trivial

## Rule

Do not start significant code changes until the plan describes:

- what the slice is
- what proof it will leave behind
- how it will be reviewed
