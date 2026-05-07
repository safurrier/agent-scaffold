---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — context-improve-refresh

## What Changed

- Root `AGENTS.md` now follows the lean context-engineering shape instead of
  duplicating the full repo map and docs index.
- Docs reference cleanup distinguishes current-repo paths from generated-output
  paths.

## Why

- Repo-root context has the strictest token budget. Detailed stack and docs
  routing belongs in `docs/`, while root `AGENTS.md` should tell a fresh agent
  what to trust, what to run, and what not to break.

## Where Reflected

- `AGENTS.md`
- `docs/AGENTS.md`
- `docs/decisions/0001-spec-driven-decision-loop.md`
- `docs/decisions/0002-plan-workflow.md`
- `docs/decisions/0003-deterministic-slice-contract.md`
- `docs/decisions/0004-skill-first-slice-workflow.md`
- `docs/decisions/0005-harden-sync-contract-ci.md`
- `docs/development.md`
- `docs/init-system.md`
- `docs/shapes.md`
- `docs/stacks/go.md`
- `docs/stacks/rust.md`
- `docs/task-contract.md`
- `templates/.ai/plans/AGENTS.md`

## Promotion

- No ADR or ledger promotion needed; this is a docs/context cleanup of existing
  contracts.
