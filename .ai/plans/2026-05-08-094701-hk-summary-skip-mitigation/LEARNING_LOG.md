---
id: plan-learning-log
title: Learning Log
description: >
  Facts, surprises, and follow-ups discovered during implementation.
---

# LEARNING_LOG — hk-summary-skip-mitigation

- The existing `hk handoff --format pr` was close to a PR summary, but a top-level `hk summary` better matches the user's mental model: `status` is for the agent loop, `summary` is for humans.
- The dogfood run initially failed readiness because decision/spec reflection was missing. That was useful: it confirmed `summary` and dangerous skips should not weaken the readiness gate.
- Summary output is clearer when no review exists but a dangerous review skip does: render `No review recorded; see dangerous review skip below` instead of just `None recorded`.
- Requiring mitigation makes tests and examples more verbose, but the added explanation is exactly what a human reviewer needs to judge the risk.
