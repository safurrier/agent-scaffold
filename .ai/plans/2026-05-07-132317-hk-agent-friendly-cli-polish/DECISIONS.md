---
id: plan-decisions
title: Decision Log
description: >
  Decisions made while implementing this unit of work.
---

# DECISIONS — hk-agent-friendly-cli-polish

## What Changed

- Generated instructions now state that `--profile` / `--profiles-dir` are discovery-only flags for `hk profile`, `hk checks`, and repo-scope `hk instructions`.
- `hk` now preflights accidental profile flags on lifecycle commands and prints repair steps before Cyclopts emits a generic unknown-option error.
- `hk ready --help` and `hk review prompt --help` now include examples.
- An agent-friendly CLI audit was recorded with remaining non-blocking gaps.

## Why

- Dogfood showed a fresh agent successfully followed the generated AGENTS.md snippet but over-generalized profile flags onto `hk start`.
- Adding no-op profile flags to lifecycle commands would blur the product model. Profile guidance should remain discovery-only unless a lifecycle command actually consumes it.
- Agent-friendly CLIs should fail fast with a correct next command, not a generic parsing error that requires extra inference.

## Where Reflected

- `src/harness_toolkit/kit/cli.py`
- `tests/unit/test_portable_workflow.py`
- `docs/agent-adoption.md`
- `docs/portable-workflow.md`
- `artifacts/agent-friendly-cli-audit.md`

## Promotion

- Slice-local only. No new ADR needed; this is a CLI/help polish decision inside the existing Harness Kit lifecycle direction.
