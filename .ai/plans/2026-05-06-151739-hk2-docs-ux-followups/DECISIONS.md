---
id: plan-decisions
title: Decisions
description: >
  Decision log for the docs-only slice.
---

# DECISIONS — hk2-docs-ux-followups

## What Changed

- `AGENTS.md` now records that HK2 should be framed primarily as an agent-facing lifecycle and handoff tool.
- `README.md` now uses an agent-workflow heading, stronger agent-facing mental model, and a compact common-command index.
- `docs/harness-kit-lifecycle-design.md` now makes the HK1 migration guide a non-goal and records a short follow-up backlog.
- `docs/portable-workflow.md` now says `hk` is not trying to be a human task manager.

## Why

- HK1 was a prototype with little usage, so HK2 does not need a migration-guide product surface.
- Humans usually direct and review; implementation agents operate the `hk` lifecycle and leave evidence.
- The advanced command index is useful, but should not become a second long manual or compete with `hk status` coaching.

## Where Reflected

- `AGENTS.md`
- `README.md`
- `docs/harness-kit-lifecycle-design.md`
- `docs/portable-workflow.md`

## Promotion

No ADR needed; this updates product framing in existing docs and repo-local agent guidance.
