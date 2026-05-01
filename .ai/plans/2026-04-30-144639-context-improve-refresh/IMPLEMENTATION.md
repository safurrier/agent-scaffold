---
id: plan-implementation
title: Implementation Plan
description: >
  Step-by-step approach for this unit of work.
  Optional — create only when the approach isn't obvious.
---

# Implementation — context-improve-refresh

## Approach

Apply the context-engineering lean default at repo root. This is a docs/context
slice: update steering files and reference hygiene, but leave Python package,
templates, task scripts, and generated behavior unchanged.

## Steps

1. Run context-engineering discovery and validation checks.
2. Rewrite root `AGENTS.md` to orientation, workflow, commands, gotchas, and
   related context.
3. Update `docs/AGENTS.md` so the agent routing index includes current stack and
   decision docs.
4. Replace stale or generated-only backticked paths with real template paths or
   plain prose.
5. Add context-engineering watermarks where validators expect them.
6. Re-run validation and close the plan evidence/review contract.
