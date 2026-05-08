---
id: plan-learning-log
title: Learning Log
---

# LEARNING_LOG — hk2-lifecycle-recenter

## Product correction

The visual explainer surfaced that HK 2.0 had been framed as a ledger-first local
assistant. That is useful, but it is not the original product goal. The goal is a
cleaner HK 1.0.

## Real HK 1.0 value

The old workflow's value is not the plan directory shape. It is the lifecycle
contract:

```text
plan + spec/decision reflection + validation evidence + external review + readiness gate + handoff artifact
```

## Better CLI shape

The memorable product surface should be:

```bash
hk start <slug>
hk context "..."
hk plan "..."
hk decide "..."
hk validate --why "..." -- <command>
hk review add --summary "..."
hk ready
hk handoff
```

## Context as product verb

`context` may be the right public verb because HK is doing context engineering:
capturing stable framing, constraints, relevant files, assumptions, and
discovered repo facts for the next human or agent. `background` may remain an
internal/migration note kind, but it is weaker as a lifecycle command.

Refinement from the design questionnaire: HK should not try to detect whether
context is required. Context should be agent-guided. The human and agent often
work out design/planning in conversation first; the agent should distill only the
context that prevents rediscovery or improves handoff. Avoid forcing the AI to
fill blank context fields for ceremony.

## One obvious way

HK 2.0 should avoid multiple equally promoted ways to do the same thing. Keep
lower-level compatibility only when it has a clear purpose:

- `hk validate` should be the promoted validation/evidence path.
- `hk capture` can remain lower-level command evidence.
- `hk note --kind ...` is questionable as public UX and should not be promoted if
  lifecycle verbs cover the common path.
- Old `hk plan/checks/sync-check` remains only until `hk ready` reaches parity,
  then should be deprecated/removed as a last step.

## Export over materialize

`export` is the better public verb for turning ledger state into shareable files
or a handoff package. `materialize` can remain internal/legacy language, but it
should not be the product word.

## Skipping readiness checks

Skipped lifecycle guarantees should feel explicit and dangerous, closer to AI
"YOLO" / dangerous permissions language than bland waiver language. Candidate
shape: `hk ready dangerously-skip review --reason "..."`. Exact naming remains
open, but the principle is captured: skipping review/validation should look like
a conscious exception.

## Profiles and dumb scripts

Profiles and dumb repo scripts still fit the design, but as guidance/stable
command surfaces rather than task runners. The flow should be:

```bash
hk profile show python
hk validate --why "Full repo quality gate." -- mise run check
hk validate --why "Focused unit coverage." -- uv run pytest tests/unit/test_harness_kit_2.py -q
```

`hk checks` can remain as a discovery/suggestion surface until parity, but HK 2.0
should not silently choose and execute checks.

## PR strategy correction

The existing PR #12 should be reshaped before merge so lifecycle commands exist
in the same PR. Landing the ledger-first UX as-is risks shipping the wrong public
product shape.

## Implication

The existing ledger/capture branch can still be valuable, but it should be
positioned as foundation until readiness parity and lifecycle verbs land.
