---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary.
---

# Learning Log

## 2026-05-06 — Redact `.ai` before merge

Plan artifacts can contain raw dogfood evidence, copied review text, and absolute local paths. Before sharing a large lifecycle PR, run a deterministic sensitive-info scan over `.ai`, not just source docs.
