---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — hk-profile-applicability-reviews

## Problem

Harness Kit profiles can list useful checks and reviews, but they do not yet help an agent answer “which of these are relevant for this diff?” Mature repos need domain-specific review/check guidance while keeping HK shell-first and advisory by default.

## Requirements

### MUST

- Profiles support optional `applies_when` and `required_when` gitignore-style path pattern arrays on `[[checks]]` and `[[reviews]]`.
- `hk checks --changed` reports changed paths and suggested checks/reviews, including matched paths and whether the item is required.
- Suggestions are advisory; HK must not execute checks or reviews.
- `hk validate --check NAME` records which profile check a validation evidence item satisfies.
- `hk review add --review NAME` records which profile review an accepted review satisfies.
- `hk review prompt REVIEW_NAME` renders a named profile review brief using `prompt_file` and live work context.
- Readiness enforces only `required_when` matches and accepts matching dangerous skips by label.
- Existing profile files remain valid without new fields.

### SHOULD

- Changed-path matching should use the active work-start SHA plus current worktree changes when active work exists.
- Error messages for unknown profile check/review names should be actionable.
- Prompt text should live in files for non-trivial reviews; profile TOML should mostly point at those files.
- The slice should dogfood an agent-friendly CLI review that applies when HK CLI command files change.

## Constraints

- Do not add `hk review run` or make HK a runner/orchestrator.
- Do not add “confidence builders” to product wording.
- Do not add a separate lightweight workflow or tell agents to skip HK for normal PR-sized work.
- Keep profile suggestions deterministic, path-based, and easy to inspect.
