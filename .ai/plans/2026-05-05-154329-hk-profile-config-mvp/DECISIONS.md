---
id: plan-decisions
title: Decisions
description: >
  Record decisions and spec reflections for this slice.
---

# Decisions — hk-profile-config-mvp

## What Changed

- Add a user-level HK profile/config MVP: one local `harness.toml` with explicit
  target bindings and inline profile/check/review guidance definitions.
- Defer repo-level `.harness` adoption, structured review backend config,
  persistent sync ignores, and automatic validation execution.

## Why

- The immediate use case is personal cross-repo/module memory for agents, not
  team-shared committed adoption.
- Profiles should describe validation/review guidance while HK remains
  shell-first and avoids becoming a task runner or review orchestrator.
- Explicit longest-prefix target resolution supports repo and module profiles
  without heuristic name/substring matching.

## Where Reflected

- Product spec: `SPEC.md`.
- HK2 design doc: `docs/harness-kit-2-design.md`.
- Portable workflow docs: `docs/portable-workflow.md`.

## Promotion

- Promote into HK2 docs as user-level config/profile guidance.
- Keep repo-level `.harness/harness.toml` documented as a future committed
  adoption layer.
