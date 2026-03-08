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
