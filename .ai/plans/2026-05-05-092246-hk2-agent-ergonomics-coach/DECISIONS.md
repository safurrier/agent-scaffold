---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — hk2-agent-ergonomics-coach

## What Changed

- Planned HK2 agent-ergonomics slice around `hk start --plan`, optional `--context`, lifecycle-only root `hk plan`, coaching `hk status`, and `dangerously-skip sync`.
- Deferred structured `--spec-ref` support to a later slice.

## Why

- PR-sized dogfood showed agents still skip or discover plan/decision records late.
- `hk start --plan` reduces command count and captures intent before coding.
- Lifecycle-only root `hk plan` removes command ambiguity with the legacy artifact workflow.
- `hk status` should catch missing lifecycle state before final readiness.
- Dangerous sync skip gives an explicit, reviewable escape hatch for local-only agent state without silently ignoring freshness.

## Where Reflected

- Slice spec: `SPEC.md`.
- Implementation plan: `IMPLEMENTATION.md`.
- Questionnaire artifact: `artifacts/design-questionnaire-summary.md`.
- Durable project docs to update during implementation: `README.md`, root `SPEC.md`, `docs/harness-kit-2-design.md`, and affected workflow docs.

## Promotion

- Pending implementation and sync.
