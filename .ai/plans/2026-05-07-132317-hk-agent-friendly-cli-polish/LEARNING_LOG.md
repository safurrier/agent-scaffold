---
id: plan-learning-log
title: Learning Log
description: >
  Facts, surprises, and follow-ups discovered during implementation.
---

# LEARNING_LOG — hk-agent-friendly-cli-polish

- The dogfood failure was not that the snippet was ignored; it was that the agent over-generalized nearby profile guidance and copied flags to `hk start`.
- This is a good fit for an actionable error, not a compatibility flag, because lifecycle commands do not use profiles directly.
- Agent-friendly CLI audit found that Harness Kit's strongest properties are non-interactive operation, broad `--json`, shell-first validation evidence, and status/ready next-action output.
- Remaining non-blocking CLI gaps are mostly polish: broad root help, non-idempotent `hk start` retries, and uneven examples on advanced subcommands.
