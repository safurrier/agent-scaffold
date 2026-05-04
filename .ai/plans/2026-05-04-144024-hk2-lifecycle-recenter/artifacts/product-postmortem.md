# HK 2.0 product-direction postmortem

## Trigger

During the HK 2.0 onboarding visual explainer review, the comparison made a key
problem visible: the current HK 2.0 implementation has useful ledger/capture
primitives, but the product framing drifted away from the original goal.

The original goal was:

> HK 2.0 should be a cleaner, simpler, more elegant version of HK 1.0.

The current branch risked becoming:

> a local agent-memory and evidence-capture product that may eventually add
> readiness parity.

That is useful, but it is not a complete replacement for HK 1.0.

## What HK 1.0 was really good at

The value was not the exact `.ai/plans/` directory or the seven Markdown files.
The value was the handoff-safety contract:

```text
plan + spec/decision reflection + validation evidence + external review + readiness gate + handoff artifact
```

The old `mise run sync-check` name was imperfect because it mixed sync and
readiness, but the contract was valuable.

## What drifted

ADR 0008 correctly identified useful implementation primitives:

- local ledger state;
- typed notes;
- command capture;
- sync freshness;
- generated handoffs;
- optional local specs.

But the public CLI shape centered those primitives directly:

```bash
hk work start
hk note --kind plan|background|learning|decision|gap|spec-impact
hk capture
hk sync
hk handoff
```

That exposes the storage model rather than the product lifecycle. It also leaves
`hk ready` as future work, which means the current shape cannot honestly replace
HK 1.0 yet.

## Correction

HK 2.0 should expose lifecycle verbs and keep the ledger behind them:

```bash
hk start <slug>
hk context "..."
hk plan "..."
hk decide "..."
hk validate --why "unit tests cover the new branch" -- uv run pytest ...
hk review add --summary "..."
hk ready
hk handoff
```

The ledger remains the right substrate. The product should feel like a simpler
HK 1.0, not a generic note ledger.

## Non-negotiables before calling it HK 2.0

1. Important context is captured when the work depends on repo facts,
   constraints, assumptions, relevant files, or prior discovery.
2. Explicit plan exists.
3. Spec/decision reflection is declared.
4. Validation evidence exists and explains what it proves.
5. External-enough review exists, or an explicit waiver/gap is declared.
6. Readiness is checked by a binary gate.
7. Handoff renders from the above.

## What remains good from the current work

The current implementation does not need to be thrown away. It provides much of
the substrate needed for the corrected direction:

- work directories and ledgers;
- event/evidence JSONL schemas;
- command transcript capture;
- sync checkpoint/diff freshness;
- generated handoff views;
- local/external state boundaries;
- optional local spec support.

The next step is to add a lifecycle-first facade and readiness semantics over
that substrate. `hk context` should be treated as a public context-engineering
verb; lower-level `background` records can remain an internal or migration
compatibility detail.

## Product principle

If `hk ready` is future work, the branch is not HK 2.0 yet. It is the
ledger/capture foundation for HK 2.0.
