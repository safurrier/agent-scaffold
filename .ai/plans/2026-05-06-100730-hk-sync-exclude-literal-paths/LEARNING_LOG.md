---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-05-06 — User correction on sync exclusions

The PR hardening pass had overcorrected `hk sync --exclude` by making `.pi` and `.claude/worktrees` the only allowed prefixes. The user clarified that the desired safety property is explicit recorded exclusions plus revalidation, not a tiny hardcoded allowlist. Adjusted the implementation to allow any literal untracked local path while keeping root/pathspec/tracked/staged/missing-path protections.

## 2026-05-06 — Dogfood result

A temp repo dogfood excluded `dist/`, `.cache/tool/`, and `src/scratch.py` while preserving a tracked README edit in the sync fingerprint. `hk sync --check` and `hk ready` passed, and the generated handoff rendered the recorded exclusions.
