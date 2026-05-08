---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — hk2-readiness-workflow

## Problem

The first HK 2.0 implementation added local ledgers, capture, sync freshness,
and generated handoffs. After dogfooding, the workflow distinction between the
new ledger loop and the original plan-artifact loop was still ambiguous.

The current scaffold `mise run sync-check` does more than sync freshness: it is a
handoff-readiness gate over plan, spec/decisions, evidence, review, and artifact
contracts. HK 2.0 should not deprecate or replace the plan-artifact workflow
until it can preserve those readiness guarantees from ledger state.

## Requirements

### MUST

- Document what the existing `mise run sync-check` contract checks: plan,
  spec/decisions, evidence, and review.
- Document that `hk sync --check` is freshness-oriented and is not equivalent to
  the existing handoff-readiness gate.
- Capture the intended lifecycle: research, plan, implement, validate, review,
  handoff.
- Describe how current plan artifacts map to future ledger-backed HK 2.0 events
  and generated views.
- Preserve the no-heuristics direction: agents choose profiles, commands, and
  review rubrics; HK records declarations and checks consistency.
- Update user-facing docs so agents understand when to use the ledger loop versus
  the plan-artifact workflow.

### SHOULD

- Name `hk ready --check` as the likely ledger-backed successor to the current
  handoff-readiness contract.
- Include review as a first-class future primitive with backend, reviewer,
  rubrics, findings, and disposition.
- Mention multiple review rubric styles such as core quality, repo conventions,
  design, UX, security, and technology-specific best practices.

## Constraints

- Do not implement the full readiness system in this slice; this is a planning
  and documentation clarification.
- Do not add heuristic validation-command detection or readiness scoring.
- Do not deprecate the original plan-artifact commands in this slice.
