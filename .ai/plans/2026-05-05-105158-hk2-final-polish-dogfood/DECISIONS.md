---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — hk2-final-polish-dogfood

## What Changed

- Planned explicit one-shot sync exclusions via `hk sync --exclude PATH --reason '...'`.
- Planned structured spec impact modes and spec refs for `hk decide`.
- Planned review ergonomics around fresh-context subagent fallback and `hk review prompt`.
- Planned status phase labels and further demotion of advanced surfaces.
- Planned less-guided three-worker PR-sized dogfood.

## Why

- `.pi`/agent-local state should not require a whole-work dangerous sync skip when the user can explicitly exclude a specific path from a checkpoint.
- Spec impact should be structured enough for status/ready/handoff to be auditable without inference.
- External review remains best, but agents need an obvious acceptable fresh-context subagent path.
- The next dogfood should validate natural discoverability rather than prompting the exact features under test.

## Where Reflected

- Slice spec: `SPEC.md`.
- Implementation plan: `IMPLEMENTATION.md`.
- Questionnaire artifact: `artifacts/design-questionnaire-summary.md`.
- Durable docs/ADR updates to make during implementation.

## Promotion

- Pending implementation and sync.
