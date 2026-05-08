---
id: plan-learning-log
title: Learning Log
description: >
  Discoveries and follow-ups found while executing the slice.
---

# LEARNING LOG — hk2-pr-sized-dogfood

- Installed `~/.local/bin/hk` is still the older command surface, so realistic
  current-HK dogfood needs either an installed updated binary or a wrapper. The
  wrapper itself caused target confusion because it uses `uv --directory`.
- Workers did naturally explore HK with `--help` before starting, matching the
  prompt.
- `hk validate --why` remains the most intuitive and useful part of the CLI.
- Workers often discover lifecycle readiness requirements late by running
  `ready`, rather than following a full lifecycle upfront.
- Review independence behaved as desired: implementation workers did not record
  same-agent self-review; final readiness stayed blocked on missing review.
- `hk evidence` as a bare group is repeatedly misused; agents expect it to list
  evidence or at least tell them to use `evidence list`.
- Legacy `sync-check` is still attractive/confusing when agents are exploring.
- Agent-local `.pi/` state in trial repos can stale sync checkpoints.
