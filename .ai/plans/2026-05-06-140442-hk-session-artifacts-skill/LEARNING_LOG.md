---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-05-06 — Skill is a better fit than wrappers

The user clarified that shell wrappers around Codex/Claude/Pi felt backwards. The better product shape is a skill that teaches agents how to find or produce exact transcript paths and attach them with `hk artifact attach`.

## 2026-05-06 — Exact paths, not latest-session automation

Captured the safety rule in the skill: use exact producer-provided paths when available; candidate discovery is a fallback and does not attach automatically.

## 2026-05-06 — Headless transcript capture works for all three sources

Verified:

- Pi can create a tiny session transcript with explicit `--session-dir`.
- Codex can stream JSONL via `codex exec --json` to a known file.
- Claude can stream JSONL via `claude -p --output-format stream-json --verbose` to a known file.

The dogfood attached all three copied transcript files and rendered them in HK handoff.
