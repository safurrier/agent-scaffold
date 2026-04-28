---
id: plan-implementation
title: Implementation Plan
description: >
  Step-by-step approach for this unit of work.
  Optional — create only when the approach isn't obvious.
---

# Implementation — slice-workflow-interface

## Approach

Refactor the deterministic slice branch toward a skill-first workflow with
`mise` as the stable command surface. Add a small stdlib helper module for prompt
rendering and status inspection, but keep it internal to task scripts rather
than exposing a second public CLI.

## Steps

1. Define the canonical `slice-workflow` generated skill with references for
   artifact policy, handoff rubric, and holdout sample tasks.
2. Convert the planner/implementer/reviewer skills into thin phase wrappers that
   point to the canonical workflow and phase-specific prompt files.
3. Add `slice-plan`, `slice-implement`, `slice-review`, and `slice-status` tasks
   that render prompts into the active plan's `prompts/` directory and optionally
   print JSON/status.
4. Add stdlib-only prompt/status helper code under `scripts/`.
5. Update task contract lists, docs, generated templates, and CI/pre-commit
   docs from 18 tasks to the new workflow task set.
6. Add tests for helper behavior, task contract existence, generated skills, and
   generated Rust docs output.
7. Run fast validation and record the exact command evidence.
