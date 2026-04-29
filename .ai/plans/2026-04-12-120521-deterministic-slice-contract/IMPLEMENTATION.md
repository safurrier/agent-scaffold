---
id: plan-implementation
title: Implementation Plan
description: >
  Step-by-step approach for this unit of work.
  Optional — create only when the approach isn't obvious.
---

# Implementation — deterministic-slice-contract

## Approach

Implement this as an extension of the existing spec-driven / plan-driven
workflow rather than a replacement. The generated repo will gain a richer plan
artifact set, five new `mise` task scripts, and an intent-structured docs tree.
The hard rule becomes "skills help produce artifacts; `mise` checks prove they
exist."

Key design points:

1. Keep `check` and `verify` focused on software validation; add `sync-check`
   for slice-completion determinism.
2. Keep plan-local working memory in `.ai/plans/<slice>/`.
3. Move durable policy and review knowledge into `docs/`.
4. Keep ADRs available, but make the default durable decision trail a repo-level
   append-only ledger.
5. Vendor workflow skills into `.agent/skills/`, but do not encode backend
   fallback chains in repo metadata.

## Steps

1. Update the active plan and add a scaffold ADR that defines the new slice contract.
2. Extend plan templates and helpers for the new required files and META schema.
3. Add shared plan-contract parsing helpers in `scripts/` and build the new
   `mise` task scripts on top of them.
4. Reshape generated docs/templates to include the context-engineering-style
   folder layout, decision ledger, and review rubric files.
5. Update generated skills and repo docs to explain how workflow skills satisfy
   the hard repo contract.
6. Expand scaffold tests for the new task list, plan artifacts, docs layout,
   and generated repo behavior.
7. Run scaffold tests, generate a Rust repo, exercise the new tasks there, and
   use a subagent to complete and review a sample slice under the new contract.
