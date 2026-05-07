---
id: plan-implementation
title: Implementation Notes
description: >
  What changed in this slice.
---

# IMPLEMENTATION — agent-adoption-doc

## Changes

- Added `docs/agent-adoption.md` as the focused reference for installing a small
  Harness Kit directive into user-level `AGENTS.md`.
- Changed `hk instructions` default output to a compact user-level directive.
- Added `hk instructions --scope repo` for the previous fuller repo-local,
  profile-specific workflow snippet.
- Replaced hardcoded workflow-file commit guidance in the repo snippet with
  generic commit hygiene for HK/agent-generated local state.
- Updated README, `docs/portable-workflow.md`, `docs/AGENTS.md`, and `mkdocs.yml`
  to point at the new agent adoption doc.
- Updated `tests/unit/test_portable_workflow.py` to cover both user and repo
  instruction scopes.

