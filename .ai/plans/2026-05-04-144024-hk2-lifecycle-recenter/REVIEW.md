---
id: plan-review
title: Review Log
description: >
  External-enough review record for this slice. Capture the backend, rubrics,
  findings, and final disposition before handoff.
---

# Review — hk2-lifecycle-recenter

## Review Context

- Mode: external
- Backend: manual_external
- Reviewer: Alex Furrier product-direction review and questionnaire

## Rubrics

- core-quality

## Findings

- The current HK 2.0 direction risked drifting from the intended goal of a
  cleaner, simpler HK 1.0.
- The old workflow's important value is the lifecycle contract, not the exact
  plan directory implementation.
- A completed HK 2.0 replacement needs `hk ready` and lifecycle-first commands;
  generic note-ledger UX alone is not enough.
- `hk context` is a plausible public verb because HK is explicitly doing context
  engineering for future humans/agents.
- `hk context` should not become ceremony or magical CLI inference. The agent
  should decide when durable context prevents rediscovery.
- Prefer one obvious promoted path; keep compatibility only when it is clearly
  advanced, legacy, or needed until parity.
- PR #12 should be reshaped before merge to include lifecycle commands.
- Subagent review found readiness blockers: failed validation evidence could pass
  readiness, rejected reviews could pass readiness, and `hk instructions` still
  described the legacy workflow. These were fixed before handoff.
- Independent subagent build trial succeeded on a synthetic tinycalc repo. The
  main UX finding was that `uv --directory ... run hk` changes cwd, so dogfood
  instructions need explicit `--target` or an installed binary.

## Disposition

- Accepted. Captured in `AGENTS.md`, `SPEC.md`,
  `docs/harness-kit-2-design.md`, ADR 0009, and
  `artifacts/lifecycle-implementation-plan.md`.
