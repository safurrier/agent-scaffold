---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-05-09

- Agents authoring module profiles often use paths relative to the selected `--target`, not the Git repo root. Supporting both coordinate systems is friendlier, but negation must be applied sequentially across both candidates so an exclude in one coordinate system cannot be bypassed by an include in the other.
- `hk profile create` should not load the user's configured catalog just to render a preset template; otherwise a missing first-time `profiles_dir` can block the command that would help create that directory's first profile.
