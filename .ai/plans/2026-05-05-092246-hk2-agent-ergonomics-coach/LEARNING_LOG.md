---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-05-05 — Questionnaire decisions

- User agreed with the proposed HK2 agent-ergonomics shape and asked to drill down, cut a slice, then run a PR-style rollout test.
- Decisions accepted: `hk start --plan`, optional `--context`, lifecycle-only root `hk plan`, coaching `hk status`, and `dangerously-skip sync`.
- User asked for clearer slug guidance and clarification of `hk plan` versus `hk start --plan`.
- Resolution: slugs are short human-readable task names; chronological ordering comes from generated timestamps/work IDs. `hk start --plan` starts work and records the first plan event; root `hk plan` records/updates lifecycle plan text for already-active HK2 work; legacy artifact creation stays under `hk legacy plan`.

## 2026-05-05 — Implementation notes

- Implemented `hk start --plan/--context` as a seeded start flow by appending normal lifecycle notes immediately after work creation.
- Removed root `hk plan` legacy fallback. If no active work exists, root `hk plan` now fails with the normal `hk start <slug>` guidance and an added `hk legacy plan <slug>` pointer.
- Implemented `hk status` as a structured local status result with readiness checks and next actions.
- Implemented sync dangerous skips as snapshot-tied events: they store event sequence and diff hash so later substantive changes make the skip stale.
