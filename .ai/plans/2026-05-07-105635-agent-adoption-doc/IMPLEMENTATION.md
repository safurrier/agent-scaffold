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

## Dotfiles adoption notes

The new doc gives generic dotfiles-managed setup steps:

1. edit the source file that syncs to user-level `AGENTS.md`;
2. paste the output of `hk instructions --scope user`;
3. run the local dotfiles or AI-config sync command;
4. start a fresh agent session;
5. test in a repo.

For the observed dots setup, likely commands are:

```bash
mise run ai-config:sync:dry-run
mise run ai-config:sync
mise run dotfiles
```
