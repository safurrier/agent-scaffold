---
id: plan-learning-log
title: Learning Log
description: >
  Durable observations that may help future work.
---

# Learning Log — hk-profiles-module-split

- Package `__init__.py` was acting as both facade and implementation. Splitting it improved locality, but tests immediately showed why a compatibility facade matters: callers relied on root-level `ProfileError` imports.
- Applicability rules are now a real module seam. Future work on harness ignore files or required-rule diagnostics should start in `profiles/applicability.py` rather than the package root.
