---
id: plan-workflow-todo
title: Plan Workflow — Task List
description: >
  Add plan-based workflow to agent-scaffold: mise task, templates, example,
  plan-sync skill, AGENTS.md convention.
---

# TODO — plan-workflow

## Phase 1: Plan Templates
- [x] Create `templates/.ai/plans/AGENTS.md` — routing index
- [x] Create plan file templates with frontmatter (META.yaml, TODO, LEARNING_LOG, VALIDATION, SPEC, IMPLEMENTATION)
- [x] Create `templates/.ai/plans/_example/` — complete example plan

## Phase 2: `mise run plan` Task
- [x] Create `.mise/tasks/plan` script
- [x] Auto-fills META.yaml with date and branch
- [x] Warns if on main
- [x] Update contract tests: plan task in CONTRACT_TASKS list

## Phase 3: `/plan-sync` Skill
- [x] Create `.agent/skills/plan-sync/SKILL.md`
- [x] Copy to `templates/.agent/skills/plan-sync/`

## Phase 4: AGENTS.md Template Update
- [x] Add "Starting Work" section with `mise run plan`
- [x] Update "Before Pushing" to include `/plan-sync`
- [x] Update scaffold's own AGENTS.md repo map

## Phase 5: Tests + Docs
- [x] Add META.yaml parser + validator to `_docs_helpers.py`
- [x] Contract tests: plan task, templates, example, META.yaml validation
- [x] Golden output tests: plan templates generated in all 4 shapes
- [x] `mise run check` green (350 passed)
- [x] Fix findings from pre-push skills (SPEC task count, docs gaps, ADR 0002)

## Phase 6: Pre-push skill fixes
- [x] Fix SPEC.md: task count 11→13, add plan requirements, add frontmatter keywords
- [x] Fix AGENTS.md: repo map 12→13, add .agent/ and .ai/ directories
- [x] Fix docs/task-contract.md: add plan and docs task rows/sections
- [x] Fix docs/index.md: add plan to task listing
- [x] Create ADR 0002 for this branch
- [x] Update plan META.yaml, TODO, LEARNING_LOG, VALIDATION
