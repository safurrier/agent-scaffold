---
id: plan-learning-log
title: Learning Log
description: >
  Discoveries, pivots, and follow-ups found while executing the slice.
---

# LEARNING LOG — hk2-review-ux-pr-trial

- User guidance: self-review prevention should not be framed as regex cat and
  mouse. The review command itself should make the rule obvious: same-agent
  self-review is not allowed; use an independent reviewer/tool or at least a
  fresh-context subagent.
- User guidance: a future dogfood trial should replay a real PR-sized change by
  rewinding a temp clone before the PR and removing forward-history cheat paths.
- `hk ready dangerously-skip ...` remains appealing, but changing command shape
  deserves a focused CLI compatibility pass instead of being bundled here.
