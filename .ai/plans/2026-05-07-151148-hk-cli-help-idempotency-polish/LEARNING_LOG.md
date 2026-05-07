---
id: plan-learning-log
title: Learning Log
description: >
  Facts, surprises, and follow-ups discovered during implementation.
---

# LEARNING_LOG — hk-cli-help-idempotency-polish

- Cyclopts does not accept extra configuration such as `group=` when registering an already-created sub-App; groups need to be set on the sub-App itself.
- Rendering examples as markdown code blocks improves captured help layout without replacing Cyclopts' help formatter.
- Same-slug retry idempotency can be implemented at the lifecycle facade without changing low-level `create_work`; this keeps direct low-level tests/behavior intact while making the promoted CLI safer for agents.
