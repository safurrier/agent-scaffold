---
id: plan-learning-log
title: Learning Log
description: >
  Discoveries, pivots, and follow-ups found while executing the slice.
---

# LEARNING LOG — hk2-dogfood-ux-fixes

- User feedback: the PR-sized dogfood process itself is valuable enough to persist
  as an in-repo development skill.
- User feedback: there appear to be many unused/confusing commands; the next
  slice should address prioritized discoverability issues from dogfood.
- Questionnaire decisions: repo-local skill only, current-HK dev shim, strict bare
  `hk evidence` with hint, move root `sync-check` under `hk legacy`, stronger
  optional context guidance, defer finish/close.
- `uv --project <harness-toolkit> run hk` preserves caller cwd, unlike
  `uv --directory`; this is the right primitive for current-checkout HK dogfood.
- Rerun result: target confusion disappeared and no worker tried `hk sync-check`.
- Rerun result: workers still tried bare `hk evidence`, but recovered after the
  new hint.
- Rerun result: lifecycle plan/decision records remain inconsistent; `ready`
  catches the gap, but agents may not iterate all the way to ready in worker
  contexts.
- Rerun result: `.pi` warnings made sync staleness clearer, but a real ignore or
  explicit override design is still unresolved.
