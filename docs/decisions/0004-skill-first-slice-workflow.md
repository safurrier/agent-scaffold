---
id: decision-skill-first-slice-workflow
title: Skill-First Slice Workflow
description: >
  Decide how generated repos expose the slice workflow: canonical skill for
  policy and judgment, mise tasks for deterministic prompt rendering and status.
index:
  - id: decision
    keywords: [slice-workflow, mise, skills, prompts, handoff, holdout]
  - id: consequences
    keywords: [provider-neutral, app-server, ci, artifacts]
---

# Decision: Skill-First Slice Workflow

## Status

Accepted.

Origin plan: `.ai/plans/2026-04-28-121022-slice-workflow-interface`.

## Context

The deterministic slice contract added plan, evidence, review, and sync checks,
plus phase skills for planning, implementation, and review. The direction was
right, but the role prompts were too thin and the workflow boundary was unclear:
some behavior lived in scripts, some in task docs, and some in separate skills.

Symphony-style orchestration is intentionally out of scope for this repo. The
next useful step is a polished one-agent workflow that works with the harness a
user already has open.

## Decision

Generated repos now expose:

- `slice-workflow` as the canonical skill for workflow policy, prompt guidance,
  artifact policy, handoff rubric, and holdout sample tasks
- `slice-planner`, `slice-implementer`, and `slice-reviewer` as compatibility
  wrappers that route users to the canonical skill and `mise` commands
- `mise run slice-plan`, `slice-implement`, `slice-review`, and `slice-status`
  as deterministic command entrypoints

The `slice-*` tasks render prompts into the active plan's `prompts/` directory.
They do not launch Codex, Claude, App Server, or any other harness in v1.

## Consequences

- Skills own judgment, rubrics, and workflow policy.
- `mise` owns deterministic file creation, prompt rendering, status output, and
  validation exit codes.
- Generated repos remain provider-neutral.
- Prompt quality can be evaluated with holdout sample tasks before it becomes a
  deterministic CI concern.
- The stable task contract grows from 18 to 22 tasks.
