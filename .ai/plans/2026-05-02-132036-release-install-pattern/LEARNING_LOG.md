---
id: plan-learning-log
title: Release Install Pattern Learning Log
description: >
  Dev diary for release/install documentation and Harness Kit dogfood.
---

# Learning Log

## 2026-05-02

- Used installed `hk` from `uv tool install --editable` to create an external plan for the release/install docs work.
- Chose the `generic` profile because Harness Toolkit has a repo-native mise contract and no exact custom profile yet.
- CI still requires committed changed plans, so the external `hk` plan was promoted into `.ai/plans/` for PR sync-check compatibility.
- Docs frontmatter validation caught a stale index id in the new release doc; fixed it before committing.
