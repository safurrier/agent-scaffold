---
id: plan-decisions
title: Decisions
description: >
  Decisions made during this slice.
---

# DECISIONS — agent-adoption-doc

## What Changed

- `hk instructions` now defaults to a compact user-level AGENTS.md snippet.
- `hk instructions --scope repo` keeps the fuller repo-local/profile-specific snippet.
- `docs/agent-adoption.md` is the focused reference for agents that are unfamiliar with HK or need install/adoption steps.

## Why

- A short user-level directive avoids loading a whole workflow manual into every agent session.
- A focused doc gives unfamiliar agents enough detail to proceed safely without pointing them at broader portable-workflow internals first.
- Reusing `hk instructions` keeps the command surface small and avoids a premature file-mutating installer.

## Where Reflected

- `src/harness_toolkit/kit/cli.py`
- `tests/unit/test_portable_workflow.py`
- `docs/agent-adoption.md`
- `README.md`
- `docs/portable-workflow.md`
- `docs/AGENTS.md`
- `mkdocs.yml`

## Promotion

- Durable docs live in `docs/agent-adoption.md` and README.
- No ADR needed; this is CLI/docs UX polish within the existing Harness Kit lifecycle direction.

## Decision: reuse `hk instructions`

Use the existing `hk instructions` command instead of adding a new top-level
`hk agents` or installer command.

### Why

The command already exists, agents can call it, and a printing-only command keeps
adoption simple. File-mutating installation can wait until we see repeated need.

## Decision: default to user-level snippet

Make `hk instructions` print the compact user-level AGENTS.md directive by
default. Keep fuller repo-local guidance behind `--scope repo`.

### Why

The current default is too long for a global user-level AGENTS.md and can nudge
agents toward `--profile generic`. The durable instruction should be small and
profile-neutral.

## Decision: add a focused doc

Add `docs/agent-adoption.md` rather than pointing agents directly at
`docs/portable-workflow.md`.

### Why

Portable workflow remains the deeper command/profile reference. Agent adoption is
a narrower job: install a short directive, handle missing `hk`, choose a target,
record validation, get review, and avoid committing local state by accident.
