---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-04-29

- Started from squash-merged `main` and confirmed open follow-up issues #6 and #7.
- Chose one branch because both issues are about making the merged contract easier
  to maintain and review.
- Kept `scripts/plan_contract.py` as the compatibility facade because the
  file-based mise tasks import it directly after putting `scripts/` on
  `sys.path`.
- Avoided adding a Click or YAML dependency for plan-contract checks. The issue
  asked for a mini-CLI shape, but the current stable interface is still the mise
  task layer, so a module boundary is the lower-risk step.
- Codex handoff review passed with no required fixes.

## 2026-04-30

- Revisited the lower-risk `scripts/` split after user feedback. The better
  boundary is skill-local: `.mise/tasks/*` stays stable, but the implementation
  moves into `templates/.agent/skills/slice-workflow/cli`.
- Added failing contract tests first for the skill-local uv CLI and task wrapper
  delegation, then moved the implementation.
- `uv run --project <skill-cli>` creates a local `.venv`; wrappers strip
  `VIRTUAL_ENV` before spawning the skill CLI to avoid noisy nested-venv
  warnings.
- Added a dedicated CLI seam test file after user feedback. The helper-level
  unit tests were not enough because they did not exercise argparse dispatch,
  module entrypoint wiring, JSON output, or expected CLI error exits.
