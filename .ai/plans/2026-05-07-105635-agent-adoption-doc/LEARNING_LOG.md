---
id: plan-learning-log
title: Learning Log
description: >
  Notes and lessons from this slice.
---

# LEARNING_LOG — agent-adoption-doc

## Notes

- `hk instructions` already existed, but its default output was effectively a
  repo-local/profile-specific snippet.
- A user-level directive should not embed `--profile generic`; agents should
  start with `hk profile resolve --target . --json` so explicit config can win.
- Simulating missing `hk` required a clean shell with `env -i` and `--noprofile
  --norc`; otherwise shell startup restored the normal PATH and found the
  installed `hk`.

## Retrospective

The split between user-level and repo-level snippets makes the CLI easier to
explain without adding a new command. `docs/agent-adoption.md` also gives a
cleaner target for future skills or installer helpers.
