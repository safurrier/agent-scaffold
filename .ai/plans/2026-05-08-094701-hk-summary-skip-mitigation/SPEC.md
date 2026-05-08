---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
---

# Specification — hk-summary-skip-mitigation

## Problem

External dogfood feedback said HK is valuable as a readiness ledger for serious agent-driven changes, but the docs/help should better explain when the ceremony pays off, planning should feel progressive rather than front-loaded, humans need a concise readiness summary, and dangerous skips should include mitigation details.

## Requirements

### MUST

- Do not add `hk quick` or a second lifecycle.
- Do not tell agents they may unilaterally skip HK or skip review for normal PR-sized work.
- Add human-facing positioning that HK is a readiness ledger for serious agent-driven changes.
- Clarify that `hk start --plan` is a convenient seed and repeated `hk plan` records are the living/progressive plan path.
- Add top-level `hk summary --target .` with Markdown output by default and JSON output with `--json`.
- Define `hk status` as the agent next-action view and `hk summary` as the human-readable readiness digest.
- Require dangerous skips to include `--label`, `--reason`, and `--mitigation`.
- Render dangerous skip label, reason, and mitigation wherever skips are surfaced for human readiness review.
- Add focused tests.
- Run one synthetic rollout dogfood test covering summary and skip mitigation.

### SHOULD

- Reuse existing ledger and handoff rendering primitives where practical.
- Keep `hk handoff` as the longer transfer artifact.
- Keep the dangerous skip verb intentionally scary.

## Constraints

- Harness Kit remains shell-first and does not choose or execute validation commands automatically.
- Review remains required by default unless explicitly and dangerously skipped.
- This is still beta; no backwards-compatibility path is required for old dangerous-skip events.
