---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-04-30

- Started from current `main` instead of the old follow-up branch so this pass
  is independent of previous PR work.
- Context-engineering reported depth 0 for root `AGENTS.md`, contributor tier
  `1`, and no relevant prior sessions.
- Reference validation exposed generated-repo paths that were backticked as if
  they were current scaffold paths. The fix is to point at real templates when
  the scaffold owns a file and use prose when the path only exists after init.
- Root `AGENTS.md` included useful material but duplicated docs routing and
  stack details. The lean shape keeps the highest-signal gotchas and routes the
  rest to docs.
- Handoff review caught an important distinction: making generated-output paths
  machine-checkable should not remove exact path contracts that agents need to
  operate generated repos. The safer pattern is exact prose for generated paths,
  backticks only for paths that exist in the current scaffold checkout.
- Folded this context pass into the existing follow-up PR branch so the
  skill-local CLI refactor, stack rubric, and context cleanup ship as one
  reviewed change set.
