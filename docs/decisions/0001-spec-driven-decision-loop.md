---
id: agent-scaffold-adr-0001
title: ADR 0001 — Spec-Driven Decision Loop
description: >
  Introduces SPEC.md as correctness envelope, ADR schema with contract tests,
  and a pre-push convention for keeping docs current via agent skills.
index:
  - id: decision
    keywords: [spec, correctness, envelope, invariants, requirements, adrs]
  - id: consequences
    keywords: [doc-split, contract-tests, skills, pre-push]
---

# ADR 0001: Spec-Driven Decision Loop

**Status**: Accepted
**Date**: 2026-03-07
**Deciders**: Alex Furrier
**Generated from**: agent-session

---

## Context

agent-scaffold generated repos with `AGENTS.md` for steering and an
architecture document for system truth, but had no document defining the
**correctness envelope** — what must always be true about any valid
implementation. The architecture document mixed normative invariants with
descriptive system state. There was also no mechanism for implementation
decisions to flow back into documentation.

Drew Breunig's "Spec-Driven Development Triangle" (2026-03-04) identified the core failure mode: specs drift because they're not synchronized with code and tests. The StrongDM Attractor NLSpec format (12 sections) provided a reference for structured specs, but was too heavy for a repo-level template.

## Decision

### Three-doc split

| Doc | What | Changes when |
|---|---|---|
| `SPEC.md` | Correctness envelope — requirements, contracts, invariants | Intent changes or new invariants discovered |
| `AGENTS.md` | How to work here — commands, repo map, workflow | Workflow or tooling changes |
| Architecture doc | System description — principles, decisions, module map | Continuously, as decisions accumulate |

### SPEC.md: 6-section structure

Distilled from NLSpec's 12 sections to what actually scales from CLI tools to large projects:

1. **Summary** — what this is
2. **Goals / Non-Goals** — scope boundaries
3. **Requirements** — MUST/SHOULD/MAY behavioral requirements
4. **Interfaces & Contracts** — public APIs, module boundaries
5. **Invariants** — rules that must always hold (heuristic: can CI prove or falsify it?)
6. **Acceptance** — how to verify

Small projects fill sections inline. Large projects use sections as routing indexes pointing to detailed docs.

### Contract test enforcement

All three doc types validated by contract tests in `mise run check`:
- SPEC.md: required sections, frontmatter schema
- Architecture.md: required sections, truth hierarchy, decisions index
- ADRs: status field (Proposed/Accepted/Deprecated/Superseded), required sections (Context/Decision/Consequences), `generated-from` traceability field

### Bottom-up spec maintenance

Instead of top-down "remember to update the spec," decisions flow back via a pre-push convention:

1. `mise run check` — hard gate (contract tests catch structural violations)
2. `/spec-sync` — agent reviews its own diff against SPEC.md, proposes ADRs
3. `/context-engineering update` — AGENTS.md updates if needed
4. `/docs-workflow update` — docs/ updates if needed

Steps 2-4 are agent skills run before pushing. No Groundskeeper orchestration needed — the agent is already in the loop.

### ADR granularity: one per PR/branch

Rather than one ADR per decision, capture decisions at the PR level — one ADR summarizing the key choices made on a branch. This keeps the decisions directory manageable while still capturing rationale.

## Consequences

**Positive:**

- Generated repos ship with a clear correctness envelope from day one
- Contract tests enforce doc standards mechanically — malformed specs fail CI
- The spec converges toward completeness over time as decisions accumulate
- Agent-agnostic: any agent that reads AGENTS.md follows the pre-push convention
- Invariants in both SPEC.md and architecture.md (redundancy is a feature for important constraints)

**Negative / Trade-offs:**

- Pre-push skill runs add friction to the push cycle (mitigated: skills are fast no-ops when nothing changed)
- ADR-per-branch may miss fine-grained decisions (acceptable for v1 — can split later if needed)
- Skills need to be installed in each repo (mitigated: scaffold generates the skill stubs)

## Alternatives Considered

| Alternative | Reason not chosen |
|---|---|
| NLSpec 12-section format | Too heavy for repo-level template — most sections empty for fresh projects |
| Groundskeeper orchestration | Over-engineered for v1 — agent convention + contract tests sufficient |
| CI-based Claude headless check | Requires API keys in CI, adds cost and latency per PR |
| PR template checklist | Weak enforcement — people ignore checklists |
| Separate SPEC.md and architecture.md invariants | Redundancy is acceptable — invariants are important enough to appear in both |
