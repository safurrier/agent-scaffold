---
id: harness-toolkit-adr-0011
title: ADR 0011 — Path-Aware Review Freshness
description: >
  Replaces exact whole-diff review freshness as the product-level readiness model
  with deterministic path/content coverage, targeted follow-up reviews, and
  export/sync validation for generated active HK handoffs.
index:
  - id: decision
    keywords: [review, freshness, path-aware, targeted-review, readiness]
  - id: consequences
    keywords: [handoff-export, sync-check, dangerous-skip, generated-artifacts]
---

# ADR 0011: Path-Aware Review Freshness

**Status**: Accepted
**Date**: 2026-05-12
**Deciders**: Alex Furrier
**Generated from**: pr

---

## Context

Harness Kit originally treated review freshness too close to an exact whole-diff
condition. That was deterministic, but dogfooding showed it created a review doom
loop during closeout:

- recording validation changed HK ledger/export state;
- regenerating `.ai/hk/<work-id>/` changed committed handoff files;
- small docs and bookkeeping edits invalidated broad review;
- the agent kept chasing freshness rather than closing out safely.

The product goal is still safety. Meaningful source-risk drift after review must
be caught. But exact whole-diff freshness is too blunt as the only readiness
model because it treats generated handoff churn and source-risk changes as the
same kind of review problem.

## Decision

Review freshness is path/content-aware instead of exact whole-diff exact.

HK records deterministic review coverage for changed paths. Readiness compares
current changed path hashes against accepted review coverage and reports
uncovered paths with targeted follow-up guidance. Agents can close review gaps
with targeted records:

```bash
hk review add --review core-review --path src/foo.py --path tests/test_foo.py \
  --backend subagent --reviewer fresh-context \
  --summary "No blockers."
```

Generated active HK handoff exports under `.ai/hk/<active-work-id>/...` are
review-neutral. ADR 0012 extends this to lifecycle freshness: active exports are
validated by export and sync checks, not by validation/review/sync freshness. This
keeps handoff regeneration from forcing another broad validation, review, or sync
loop while preserving deterministic integrity checks for generated artifacts.

`hk dangerously-skip review` remains available for explicit exceptions, such as
an external review tool being unavailable. The skip must record a reason and a
mitigation, and it remains visible in readiness and handoff output.

## Consequences

Positive outcomes:

- avoids broad review thrash during final closeout;
- preserves deterministic drift detection for meaningful changed paths;
- makes readiness diagnostics actionable by naming uncovered paths;
- supports targeted follow-up reviews after small fixes;
- validates generated handoff artifacts with checks that understand their shape.

Trade-offs:

- path-level coverage is more complex than one whole-diff hash;
- semantic coupling across paths may still require broad review by judgment or
  profile policy;
- generated/export validation must stay strict because generated active handoff
  exports are no longer validation, review, or sync blockers;
- profiles may need to require broad review for high-risk areas even when path
  coverage exists.

## Alternatives Considered

| Alternative | Reason not chosen |
|---|---|
| Keep exact whole-diff review freshness | Deterministic, but caused closeout loops on generated artifacts and bookkeeping changes. |
| Disable review freshness entirely | Too unsafe; meaningful source changes after review must still be caught. |
| Always rerun full review after every final edit | Safe but too expensive and noisy for agent workflows. |
| Treat all docs/generated files as ignored | Too broad; docs and specs can be product-relevant and should sometimes be reviewed. |

## Follow-up

- Consider dependency-aware or path-group review coverage for changes where one
  file semantically invalidates review of another.
- Keep profile-required review coverage explicit rather than inferring all review
  needs from path hashes.
- Continue hardening export and sync validation for generated handoff artifacts.
