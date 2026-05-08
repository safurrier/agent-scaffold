---
id: plan-decisions
title: Decisions
description: >
  Decision log for this slice. Include what changed, why, and where the durable
  record lives.
---

# Decisions — hk2-review-ux-pr-trial

## What Changed

- `hk review add` UX now states that self-review does not satisfy readiness.
- Obvious same-agent/self-review identities are rejected before they enter new
  ledgers.
- Readiness guidance now tells agents to get independent/fresh-context review or
  use an explicit dangerous skip.
- The next PR-sized dogfood trial shape is captured for follow-up.

## Why

- Real-repo dogfood showed agents will try to satisfy review readiness with
  same-agent self-review-ish labels if the command shape allows it.
- The product goal is not to win regex cat-and-mouse against agent wording. The
  durable guarantee is a clearly communicated review rule: same-context
  self-approval does not count.
- The review gate should push agents toward a separate human/tool or at least a
  fresh-context subagent, and otherwise force a scary explicit skip.
- The next useful validation step is a PR-sized replay trial, not more toy repos.

## Where Reflected

- `src/harness_toolkit/kit/cli.py`
- `src/harness_toolkit/kit/local.py`
- `tests/unit/test_harness_kit_2.py`
- `AGENTS.md`
- `README.md`
- `SPEC.md`
- `docs/harness-kit-lifecycle-design.md`
- `.ai/plans/2026-05-04-200933-hk2-review-ux-pr-trial/artifacts/pr-sized-dogfood-plan.md`

## Promotion

- Ready for sync after focused tests, full `mise run check`, and fresh-context
  reviewer subagent review.
