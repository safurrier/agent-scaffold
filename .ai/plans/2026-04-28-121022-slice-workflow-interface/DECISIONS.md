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

- `docs/decisions/0004-skill-first-slice-workflow.md`
- `templates/.agent/skills/slice-workflow/`
- `templates/.agent/skills/slice-planner/SKILL.md`
- `templates/.agent/skills/slice-implementer/SKILL.md`
- `templates/.agent/skills/slice-reviewer/SKILL.md`
- `docs/task-contract.md`
- `mkdocs.yml`
- `templates/README.md.tmpl`
- `templates/AGENTS.md.tmpl`
- `templates/SPEC.md.tmpl`
- `tests/unit/test_slice_workflow.py`
- `tests/contract/test_task_contract.py`
- `tests/e2e/test_python.py`

## Promotion

- Promote as an ADR because this changes the generated task contract and agent
  workflow architecture.
