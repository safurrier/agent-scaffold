---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — deterministic-slice-contract

## Problem

`agent-scaffold` currently creates lightweight plans and relies on soft skills
(`/plan-sync`, `/spec-sync`, `/context-engineering update`) to keep work from
stalling half-finished. That was not strong enough in Foreman: the useful parts
were the plan trail, heavy validation, evidence artifacts, and docs sync, but
the scaffold did not mechanically require those outcomes. The scaffold needs a
generic, deterministic slice contract that works across stacks without
hard-coding a TUI-specific workflow.

## Requirements

### MUST

- Generated repos keep `mise run check` as the fast engineering gate and add a
  separate deterministic handoff gate for plan/spec/evidence/review checks.
- `mise run plan -- <slug>` creates a richer plan directory that includes
  machine-checkable review and evidence placeholders, not only TODO/learning log
  stubs.
- The plan metadata schema captures contract intent (`contract_change`),
  decision handling (`decision_record`), evidence expectations, and review
  policy so the repo can validate completion mechanically.
- Generated repos ship an intent-structured docs layout with durable locations
  for architecture, decision ledger entries, and review rubrics.
- The scaffold vendors workflow skills as repo-local helpers, but the hard
  contract is enforced by `mise` tasks rather than by skill instructions alone.
- The scaffold adds tests that fail if the new plan/task/doc contract drifts.
- The generated repo must support an end-to-end slice where a distinct reviewer
  execution context leaves behind persistent review and evidence artifacts.

### SHOULD

- The new contract should keep existing concepts where they still pay off:
  learning logs stay, ADRs remain available for high-impact decisions, and
  generated repos still get an initial stack-choice ADR.
- The new docs structure should adopt the context-engineering intent taxonomy
  (`tutorials`, `how-to`, `explanation`, `reference`) without forcing large
  amounts of filler content on day one.
- Review rubrics should live under docs so they can evolve like any other
  durable project knowledge.
- The new `mise` checks should share one parser/helper surface instead of
  re-implementing plan parsing independently in each task.

## Constraints

- Keep the scaffold generic. Do not bake in TUI- or tmux-specific validation.
- Avoid heavy runtime dependencies for parsing plan metadata or manifests; use
  stdlib-friendly formats and helpers.
- Do not fold the handoff checks into `mise run check`; preserve a fast inner
  loop and a stronger completion gate.
- Preserve the scaffold’s current ability to initialize Python, Go, and Rust
  projects cleanly.
