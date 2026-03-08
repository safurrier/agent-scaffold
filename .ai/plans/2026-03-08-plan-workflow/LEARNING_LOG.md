---
id: plan-workflow-learning-log
title: Plan Workflow — Learning Log
description: >
  Dev diary for building the plan workflow feature.
---

# Learning Log

## 2026-03-08 — Design decisions from conversation

Key decisions made before implementation:

- **4 required files, 2 optional**: META.yaml, TODO.md, LEARNING_LOG.md, VALIDATION.md required. SPEC.md and IMPLEMENTATION.md optional for heavier work.
- **META.yaml for machine-readable metadata**: Separate structured file instead of embedding in TODO frontmatter. Enables future tooling (Groundskeeper, dashboards).
- **VALIDATION.md as verification log**: Points to artifacts, doesn't store them. Completes the triangle at plan level (SPEC = what, TODO = tasks, VALIDATION = proof).
- **Branch naming is agent's job**: `mise run plan` creates the directory but doesn't create/name branches. Semantic naming needs context the script doesn't have.
- **Example plan as reference**: `_example/` directory shows agents what good plans look like. Referenced from `.ai/plans/AGENTS.md`.
- **Learning log is a dev diary**: Append timestamped entries during work, not just retrospective at completion. Captures user feedback and course corrections.

## 2026-03-08 — Implementation went clean

Built all 5 phases in one pass. No surprises:
- Plan task script follows the same pattern as other mise tasks (uv shebang, lib imports)
- Templates use `{{slug}}`, `{{branch}}`, `{{created}}` placeholders — consistent with Jinja2 but actually just string replacement in the plan task (no Jinja dependency)
- Had to add `.ai/plans/` copy to `generate_docs()` in common.py, same pattern as skills copy
- Added `plan` and `docs` to CONTRACT_TASKS — bumped task count from 12 to 13 everywhere

## 2026-03-08 — Pre-push skills found real issues (again)

Ran all 4 pre-push skills. Findings:
- SPEC.md still had "All 11 task scripts" in MUST requirements (missed in earlier count fix)
- AGENTS.md repo map was missing .agent/ and .ai/ directories
- docs/task-contract.md had no plan or docs task documentation
- docs/index.md code block didn't show plan command
- No ADR for this branch
- Plan's own META.yaml, TODO, LEARNING_LOG all stale

Same pattern as last PR — the skills consistently find real drift. The pre-push convention works.
