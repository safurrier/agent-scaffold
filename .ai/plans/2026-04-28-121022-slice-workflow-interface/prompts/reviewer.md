# Slice Reviewer Prompt

Phase: reviewer
Plan: `.ai/plans/2026-04-28-121022-slice-workflow-interface`
Branch: `feat/deterministic-slice-contract`

Use the `slice-workflow` skill. You are reviewing this slice before handoff.
Treat the review as verification, not self-assurance.

## Current Plan Context

## SPEC.md

---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — slice-workflow-interface

## Problem

The deterministic slice contract branch has the right direction but the workflow
is split across low-depth phase skills, validation scripts, and docs. The
operator-facing shape should be clearer:

- skills own the workflow, judgment, rubrics, and prompt policy
- `mise` tasks own deterministic command entrypoints
- prompt rendering is provider-neutral and does not launch Codex, Claude, or an
  app-server in v1
- evidence and handoff files are durable, while raw transcripts, giant diffs,
  and scratch artifacts stay out of the durable repo context

This must build on the current stacked branch, including the Rust stack work.

## Requirements

### MUST

- Add a canonical slice workflow skill that explains planning, implementation,
  review, artifact policy, and holdout sample tasks.
- Keep `slice-planner`, `slice-implementer`, and `slice-reviewer` as thin
  compatibility entrypoints or replace them with an equivalent discoverable
  phase interface.
- Add deterministic `mise` task entrypoints for rendering phase prompts and
  reporting slice status.
- Keep v1 provider-neutral: render prompts to files/stdout; do not launch a
  coding harness.
- Include deterministic tests for new task files, prompt rendering, generated
  repo output, and Rust-stack generated repos.
- Update README, AGENTS, task-<REDACTED_TOKEN> docs, SPEC/templates, and CI/task
  contract expectations so source and generated repos agree.
- Add holdout sample task fixtures or docs that can be used to evaluate prompt
  quality without blocking normal CI.
- Fix obvious docs drift from the Rust branch while touching the generated docs
  contract.

### SHOULD

- Prefer stdlib Python for task helpers so generated Go/Rust projects do not
  need extra Python dependencies to run workflow tasks.
- Avoid a public Python CLI for v1; if helper logic is needed, keep it behind
  the `mise` task surface.
- Use deterministic checks for CI blockers and keep fuzzy stale-doc or prompt
  quality checks as warnings/manual evals.

## Constraints

- Do not implement Symphony-style orchestration, issue polling, app-server
  sessions, background agents, or automatic harness launch.
- Do not make generated repos depend on a Python package install just to render
  prompts.
- Do not retain plan-local scratch artifacts as durable context unless they are
  intentionally summarized or declared.

---

## IMPLEMENTATION.md

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

---

## TODO.md

---
id: plan-todo
title: Task List
description: >
  Checkable tasks for this unit of work. Check off as you go.
  See _example/ for a reference.
---

# TODO — slice-workflow-interface

- [ ] Add canonical generated `slice-workflow` skill, phase wrappers, and references.
- [ ] Add stdlib prompt-rendering/status helper behind `mise` tasks.
- [ ] Add `slice-plan`, `slice-implement`, `slice-review`, and `slice-status` task files.
- [ ] Update docs/templates/specs/task-<REDACTED_TOKEN> references, including Rust stack docs drift.
- [ ] Add holdout sample task fixtures/docs for prompt-quality regression review.
- [ ] Add or update unit/contract/e2e tests.
- [ ] Run fast validation and update `VALIDATION.md`.
- [ ] Complete review/handoff evidence.

---

## DECISIONS.md

---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — slice-workflow-interface

## What Changed

- The slice workflow becomes skill-first: a canonical `slice-workflow` skill owns
  the workflow, rubrics, prompt policy, artifact policy, and holdout examples.
- `mise` remains the public command surface for deterministic actions.
- Any Python helper remains internal to the task surface for v1, not a second
  user-facing CLI.
- V1 renders prompts for the user's existing harness instead of launching Codex,
  Claude, or app-server sessions.

## Why

- This preserves the easy "anyone can run the task" interface while avoiding a
  pile of one-off scripts or low-quality phase prompts.
- It keeps generated repos provider-neutral.
- It gives CI deterministic things to check without pretending fuzzy prompt
  quality can be fully mechanized.

## Where Reflected

- New ADR under `docs/decisions/`.
- Generated skill references under `templates/.agent/skills/slice-workflow/`.
- Task contract docs and templates.
- Unit/contract/e2e tests.

## Promotion

- Promote as an ADR because this changes the generated task contract and agent
  workflow architecture.

## Your Job

1. Read `META.yaml`, `TODO.md`, `VALIDATION.md`, `DECISIONS.md`, and the changed
   files.
2. Load the rubrics named in `META.yaml` from `docs/reference/review-rubrics/`
   when present.
3. Check whether the implementation, docs, generated templates, tests, and
   validation evidence agree.
4. Write findings into `REVIEW.md` with:
   - mode
   - backend
   - reviewer
   - rubrics
   - findings
   - disposition
5. Update `META.yaml` `review_backend` to match the review artifact.

## Review Standard

Fail the handoff if required evidence is missing, generated docs drift from the
source contract, or the plan is marked complete before the actual PR/review state
supports it.
