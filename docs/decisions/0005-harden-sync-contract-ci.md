---
id: agent-scaffold-adr-0005
title: ADR 0005 — Harden Sync Contract CI
description: >
  Clarifies that sync-check has local active-plan semantics and PR changed-plan
  semantics, and that small committed evidence artifacts are preferred over
  ignored scratch evidence.
index:
  - id: decision
    keywords: [sync-check, ci, changed-plans, evidence, artifacts]
  - id: consequences
    keywords: [completed-plans, bootstrap-lockfiles, manifest]
---

# ADR 0005: Harden Sync Contract CI

**Status**: Accepted
**Date**: 2026-04-29
**Deciders**: Alex Furrier
**Generated from**: external review feedback
**Plan**: `.ai/plans/2026-04-29-134035-harden-sync-contract-ci/`

---

## Context

The first deterministic slice contract validated active `planned` or
`in-progress` plans well during local work. PR CI used the same default mode,
which meant completed plans on a branch could produce a misleading green result:
there was no active plan to validate, so sync-check passed without checking the
completed plan evidence.

External review also found that generated Rust apps repos could fail sync-check
after setup because module-local `Cargo.lock` files were treated as meaningful
unplanned work.

Finally, ignored scratch artifacts made the committed evidence story less clear:
validation logs referenced artifact manifests, but the manifests could be empty.

## Decision

Sync-check now has two explicit modes:

- default local mode validates the active plan and catches unplanned working-tree
  changes
- `--changed-plans <git-refspec>` validates completed plan directories changed
  by a branch, which is what PR CI runs

Individual contract tasks also accept `--plan-dir` so sync-check can validate a
specific completed plan without pretending it is active.

Plan artifact policy is tightened:

- `artifacts/manifest.yaml` remains committed
- small top-level `.md`, `.txt`, `.log`, and `.png` evidence artifacts may be
  committed when useful
- raw scratch subtrees remain ignored
- a manifest entry is a promise that the referenced file exists and is tracked
  or staged for commit

Setup-generated lockfiles named `Cargo.lock`, `go.sum`, or `uv.lock` are treated
as local working-tree bootstrap noise regardless of module depth. Branch
`--changed-plans` mode does not ignore lockfile-only diffs; dependency changes
still require a plan.

PR mode requires every changed plan to be marked `status: complete`.

## Consequences

**Positive:**

- PR CI validates completed plans changed by the branch.
- Generated apps repos can run setup before sync-check without false unplanned
  lockfile failures.
- Reviewers can inspect compact committed evidence without chasing ignored local
  scratch paths.

**Negative / Trade-offs:**

- CI needs enough git history to diff against the PR base.
- The sync-check task has more modes to document and test.
- Teams still need judgment about which evidence artifacts are worth committing.

## Alternatives Considered

| Alternative | Reason not chosen |
|---|---|
| Keep CI in active-plan mode only | Too easy for completed plans to escape validation |
| Add a separate `sync-check-pr` task | More task surface area; flags preserve the stable task list |
| Commit every artifact under `artifacts/` | Too much raw transcript and scratch noise |
