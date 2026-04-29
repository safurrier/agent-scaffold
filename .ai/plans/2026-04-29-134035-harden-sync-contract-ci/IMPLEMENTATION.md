---
id: plan-implementation
title: Implementation Plan
description: >
  Step-by-step approach for this unit of work.
  Optional — create only when the approach isn't obvious.
---

# Implementation — harden-sync-contract-ci

## Approach

Keep the existing active-plan task model, but add explicit plan targeting:

- individual contract tasks accept --plan-dir for completed-plan validation
- sync-check keeps its default active-plan mode
- sync-check adds --changed-plans <git-refspec> for PR CI, selecting changed .ai/plans directories, requiring status: complete, and validating each one
- local plan bootstrap-noise filtering expands from root lockfiles to lockfiles at any generated module depth
- PR changed-plan mode keeps lockfile diffs meaningful so dependency-only PRs still require a plan
- evidence-check rejects manifest paths ignored by git
- artifact ignore rules allow small top-level durable evidence files while continuing to ignore scratch subtrees

## Steps

1. Add plan selection helpers and nested bootstrap-noise filtering to scripts/plan_contract.py.
2. Update plan/spec/evidence/review tasks to accept --plan-dir.
3. Update sync-check to support --plan-dir and --changed-plans.
4. Update CI workflows to run changed-plan validation on pull requests.
5. Update artifact ignore rules, docs, and generated templates.
6. Backfill small committed evidence artifacts for completed plans.
7. Add tests for helper behavior, generated CI, and Rust apps sync-check after setup.
