---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-05-06 — Codex review hardening loop

- Codex 4-pass review repeatedly found concrete HK2 sync/readiness edge cases that local parity tests had not covered yet.
- Added regression coverage for constrained sync exclusions, tracked descendants under agent-local paths, strict ledger/evidence JSONL shape validation, PR handoff dangerous-skip disclosure, scoped spec promotion, and symlink identity hashing.
- Kept pushing only after the final focused Codex pass reported no code-correctness blockers; remaining doc wording was aligned before handoff.
