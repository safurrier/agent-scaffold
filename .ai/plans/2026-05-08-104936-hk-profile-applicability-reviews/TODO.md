---
id: plan-todo
title: Task List
description: >
  Checkable tasks for this unit of work. Check off as you go.
  See _example/ for a reference.
---

# TODO — hk-profile-applicability-reviews

- [x] Add optional `applies_when` / `required_when` fields to profile checks and reviews.
- [x] Add changed-path matching for active HK work based on work-start SHA plus current worktree changes.
- [x] Add `hk checks --changed` suggestions for applicable/required checks and reviews without executing anything.
- [x] Add `hk validate --check NAME` so agents can bind evidence to a named profile check.
- [x] Add `hk review add --review NAME` so agents can bind accepted review evidence to a named profile review.
- [x] Add named `hk review prompt REVIEW_NAME` rendering that uses `prompt_file` plus live work context.
- [x] Enforce required applicable profile checks/reviews in `hk ready`, allowing matching dangerous skips by label.
- [x] Dogfood with an agent-friendly CLI review profile that triggers when command files change.
- [x] Update docs/tests and run validation/review.
