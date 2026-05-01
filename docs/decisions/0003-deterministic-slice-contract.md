---
id: agent-scaffold-adr-0003
title: ADR 0003 — Deterministic Slice Contract
description: >
  Extends the scaffold with explicit plan/spec/evidence/review checks, an
  append-only decision ledger, review rubrics, and vendored workflow skills.
index:
  - id: decision
    keywords: [sync-check, evidence, review, ledger, rubrics, plans]
  - id: consequences
    keywords: [task-contract, docs-structure, vendored-skills, handoff]
---

# ADR 0003: Deterministic Slice Contract

**Status**: Accepted
**Date**: 2026-04-12
**Deciders**: Alex Furrier
**Generated from**: agent-session
**Plan**: `.ai/plans/2026-04-12-120521-deterministic-slice-contract/`

---

## Context

ADR 0001 and ADR 0002 introduced a spec-driven loop and a plan-based workflow,
but the generated repos still relied too heavily on soft agent conventions to
close the loop. In practice, the useful outcomes were:

- a current slice plan
- durable doc updates
- explicit evidence artifacts
- external-enough review

Those outcomes were not enforced mechanically. Agents could still leave slices
half done: code changed, but no review artifact, no promoted decision note, or
no evidence bundle.

## Decision

Extend the scaffold with a deterministic slice contract:

- add `mise run plan-check`, `spec-check`, `evidence-check`, `review-check`, and
  `sync-check`
- extend plan templates with `REVIEW.md`, `DECISIONS.md`, and an artifact
  manifest
- replace blanket ADR expectations with `decision_record: none | ledger | adr`
- generate an append-only repo decision ledger plus review rubrics from
  `templates/docs/reference/review-rubrics/`
- vendor workflow skills (`slice-planner`, `slice-implementer`, `slice-reviewer`,
  context helpers) into generated repos, while keeping the hard contract in
  `mise` rather than in prompts alone
- initialize generated docs with an intent structure
  (`tutorials`, `how-to`, `explanation`, `reference`)

## Consequences

**Positive:**

- Generated repos can mechanically reject half-finished slices.
- Decision history becomes readable without forcing full ADR ceremony every time.
- Review standards become durable repo knowledge, not ephemeral reviewer taste.
- Vendored skills remain useful, but are no longer the only enforcement mechanism.

**Negative / Trade-offs:**

- The task contract grows, so docs and tests must track more surface area.
- Plans become more structured, which adds overhead for trivial changes.
- The generated docs tree is larger on day one than the previous minimal setup.

## Alternatives Considered

| Alternative | Reason not chosen |
|---|---|
| Keep the old `plan-sync` / `spec-sync` convention only | Too easy to skip; not deterministic enough |
| Require a full ADR for every meaningful slice | Creates document churn and low-value ADR noise |
| Put review rubrics in `.agent/skills/` only | Review standards should evolve as repo knowledge, not only as harness prompts |
