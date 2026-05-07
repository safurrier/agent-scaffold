---
id: plan-learning-log
title: Learning Log
description: >
  Notes and lessons from this slice.
---

# LEARNING_LOG — hk-agent-adoption-dogfood

## What happened

- The agent followed the compact snippet without the prompt mentioning HK or AGENTS.md.
- It started by resolving the profile, then explored instructions/profile list/brief.
- It tried one invalid command: passing `--profile` and `--profiles-dir` to `hk start`.
- It recovered and completed the lifecycle through ready/handoff.

## Lessons

- The short snippet is enough for Codex to pick up HK behavior from AGENTS.md.
- Profile-related flags remain a UX trap when agents infer they should apply everywhere.
- Root `AGENTS.md` is still useful after the PR, but some product rationale could eventually move into docs for progressive disclosure.
