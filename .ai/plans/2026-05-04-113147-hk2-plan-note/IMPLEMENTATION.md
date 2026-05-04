---
id: plan-implementation
title: Implementation Plan
description: >
  Step-by-step approach for this unit of work.
  Optional — create only when the approach isn't obvious.
---

# Implementation — hk2-plan-note

## Approach

Add a small deterministic CLI primitive rather than a fuzzy adoption command.
Agents remain responsible for interpreting external conversations/plans and can
record the distilled result as a `plan` note, either inline or from a file.

## Steps

1. Extend valid note kinds and CLI `Literal` choices with `plan`.
2. Add `--from-file` to `hk note`, with mutual exclusion against positional text.
3. Render `plan` and `context` sections in handoff output.
4. Materialize `views/plan.md` and `views/context.md` alongside existing views.
5. Update docs and spec to explain external planning translation through explicit
   plan/context/decision notes.
6. Add focused unit/CLI tests.
7. Run focused tests, full check, sync-check, and external review.
