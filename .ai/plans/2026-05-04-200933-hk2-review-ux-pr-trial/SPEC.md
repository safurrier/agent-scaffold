---
id: plan-spec
title: Scope Specification
description: >
  Slice-local scope and acceptance criteria. Link durable repo specs when the
  change affects public behavior.
---

# SPEC — hk2-review-ux-pr-trial

## Problem

Real-repo HK 2.0 dogfood showed that agents can satisfy the review gate with
self-review-ish identities unless the CLI makes the policy impossible to miss.
Regex rejection catches common cases, but the product should not rely on a
cat-and-mouse detector. The main prevention mechanism should be clear command
wording, generated snippets, readiness messages, and docs: self-review does not
count; agents must get an independent reviewer or at least a fresh-context
subagent review.

## Scope

- Improve review UX/help/docs so `hk review add` clearly represents an
  independent review record.
- Keep heuristic rejection for obvious self-review identities as a guardrail.
- Update readiness messaging to direct agents toward a separate reviewer/subagent
  or an explicit dangerous skip.
- Capture the proposed next-stage PR-sized dogfood trial plan.

## Out of scope

- A full `hk ready dangerously-skip ...` command restructure.
- Profile versus `.harness/harness.toml` design.
- Actually running the Discord/Discord-AI-shaped PR-sized trial in this slice.

## Acceptance

- `hk review add --help` and generated agent snippets say self-review does not
  count.
- Obvious self-review identities are rejected before they enter new ledgers.
- `hk ready` gives actionable review guidance if recorded review data does not
  satisfy readiness.
- Repo docs preserve the product rule that fresh-context/independent review is
  the guarantee and heuristics are only guardrails.
- Tests and `mise run check` pass.
