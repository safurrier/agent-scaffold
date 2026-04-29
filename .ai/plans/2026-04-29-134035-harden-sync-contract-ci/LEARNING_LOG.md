---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-04-29

- External review was directionally right: the active-plan-only sync-check mode
  was useful locally but too weak for PR CI.
- Generated Rust apps surfaced a concrete bootstrap-noise bug because setup
  creates per-module Cargo.lock files before any plan exists.
- The artifact policy needed to move from "only manifest is committed" to
  "manifest plus small durable summaries are committed; scratch remains ignored."
