---
id: plan-learning-log
title: Learning Log
description: >
  Durable observations that may help future work.
---

# Learning Log — hk-profile-applicability-reviews

- Review instructions should stay file-backed. Normal profile/check JSON should expose `prompt_file`, not the full prompt contents; `hk review prompt REVIEW_NAME` is the right place to render prompt file text with live work context.
- Required profile suggestions need an explicit enforcement boundary. Discovery-only `--profile` / `--profiles-dir` views can describe what a profile would require, but readiness can only enforce the target's resolved lifecycle profile from user config.
- Path glob semantics matter for readiness. Full-path `fnmatch` is too broad for repo policy rules because `*.md` matching nested docs and `github/**` matching `.github/**` can create surprising readiness blockers.
- Named checks/reviews are durable IDs, so profile parsing should reject duplicate or shell-hostile names early.
