---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — harden-sync-contract-ci

## What Changed

- Tighten sync-check from an active-plan-only handoff gate into a dual-mode gate: local active-plan validation by default, changed-plan validation for PR CI.
- Treat committed artifact summaries as normal durable evidence and leave scratch artifact trees ignored.
- Treat setup-generated nested lockfiles as bootstrap noise so generated apps repos do not need a plan immediately after setup.

## Why

- CI should validate completed plan artifacts added by a branch, not only report that there is no active plan.
- Reviewers should be able to trust committed plan evidence without chasing ignored local scratch directories.
- Generated repos should pass their own CI after setup without requiring agents to explain tool-generated lockfiles as meaningful work.

## Where Reflected

- `docs/decisions/0005-harden-sync-contract-ci.md`
- `docs/task-contract.md`
- `docs/ci.md`
- `templates/.ai/plans/AGENTS.md`
- `templates/.agent/skills/slice-workflow/references/artifact-policy.md`
- `.github/workflows/ci.yml`
- `templates/.github/workflows/ci.yml.tmpl`

## Promotion

- Durable rationale promoted to `docs/decisions/0005-harden-sync-contract-ci.md`.
