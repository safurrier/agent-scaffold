---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — hk2-pr-sized-dogfood

## What Changed

- Ran PR-sized dogfood trials in temp snapshots instead of toy repos.
- Captured the actual HK command path through a wrapper log and worker reports.
- Recorded concrete HK UX findings for lifecycle onboarding, target handling,
  evidence listing, legacy command confusion, review readiness, and sync
  freshness.

## Why

- The previous tiny trials validated the happy path but did not show how agents
  behave on larger implementation tasks.
- The user wanted minimal HK prompting so the study would reveal natural CLI
  discovery and misuse.
- Parallel PR-sized tasks expose whether HK helps when agents are busy with real
  code complexity and environment blockers.

## Where Reflected

- `.ai/plans/2026-05-04-230243-hk2-pr-sized-dogfood/artifacts/pr-sized-dogfood-study.md`

## Promotion

- This is a research/dogfood artifact. Product fixes discovered here should be
  split into follow-up implementation slices.
