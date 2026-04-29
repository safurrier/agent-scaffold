---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — harden-sync-contract-ci

## Problem

External review found that the branch's sync contract is weaker than advertised:

- generated Rust apps repos can fail sync-check after setup because nested Cargo.lock files are treated as unplanned work
- CI sync-check validates only active plans, so completed plans added on a PR can escape contract validation
- committed plan validation logs can point at artifact manifests that are empty, making the evidence trail less durable than it claims

## Requirements

### MUST

- Preserve local sync-check behavior for active planned/in-progress slices.
- Add a PR/changed-plan mode that validates completed plan directories changed by a branch.
- Make generated CI use the PR/changed-plan mode for pull requests.
- Require changed plans to be `status: complete` before PR-mode sync-check passes.
- Treat setup-generated nested lockfiles as bootstrap noise for plan-check.
- Do not treat branch lockfile diffs as bootstrap noise; dependency changes still require a plan.
- Keep small durable evidence artifacts committed and declared in artifacts/manifest.yaml.
- Reject manifest entries that point at git-ignored artifact paths.
- Keep scratch plan artifacts ignored.
- Add tests covering nested lockfile noise and completed-plan validation selection.

### SHOULD

- Keep task names stable; prefer flags over introducing a new required task.
- Keep the artifact policy simple enough for generated repos to understand.
- Backfill existing completed plans on this branch so they satisfy the tightened policy.

## Constraints

- Do not build an orchestrator.
- Do not require network access for sync-check itself.
- Avoid fuzzy prose-quality checks; validate concrete files, paths, metadata, and command evidence.
