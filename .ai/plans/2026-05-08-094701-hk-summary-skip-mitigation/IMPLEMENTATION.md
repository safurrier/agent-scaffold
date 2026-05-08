---
id: plan-implementation
title: Implementation Notes
description: >
  What changed and where.
---

# IMPLEMENTATION — hk-summary-skip-mitigation

## Summary command

Added a top-level `hk summary` command in `src/harness_toolkit/kit/cli.py` backed by `LifecycleApp.summary` and `local.summary`.

The summary renderer lives in `src/harness_toolkit/kit/rendering/handoff.py` and produces Markdown by default with:

- work/branch/SHA/readiness/sync/dirty overview;
- plan entries;
- validation evidence with transcript references;
- review records or a pointer to a dangerous review skip;
- dangerous skip label/reason/mitigation;
- attached artifacts;
- readiness checks.

`--json` returns the existing dataclass shape with `work_id`, `content`, and `path`.

## Dangerous skip mitigation

`hk dangerously-skip` now requires:

- `--label`
- `--reason`
- `--mitigation`

The local ledger event now records those fields, and event validation requires them for `dangerous_skip_added`. Readiness messages and handoff/summary renderers include the label and mitigation.

## Docs and help

Updated:

- `README.md`
- `docs/agent-adoption.md`
- `docs/portable-workflow.md`
- `docs/harness-kit-lifecycle-design.md`
- `docs/decisions/0009-harness-kit-lifecycle-first-cli.md`
- review prompt guidance
- generated `hk instructions` snippets

The docs position HK as a readiness ledger for serious agent-driven changes, explain progressive planning with repeated `hk plan`, and distinguish:

- `hk status`: agent next-action loop;
- `hk summary`: concise human-readable readiness digest;
- `hk handoff`: longer transfer artifact.

## Tests

Updated and added tests for:

- dangerous skip label/mitigation requirements;
- dangerous skip rendering in handoff/PR handoff;
- `hk summary` output;
- existing generated-instruction and portable workflow behavior;
- lifecycle parity tests using the new dangerous-skip shape.

## Dogfood

Ran a synthetic rollout dogfood in `/tmp/hk-summary-skip-dogfood/repo` covering:

- `hk start` without an upfront plan;
- same-slug retry resume;
- repeated `hk plan` progressive planning;
- `hk validate` evidence capture;
- `hk dangerously-skip review --label ... --reason ... --mitigation ...`;
- `hk sync`, `hk ready`, and `hk summary`.

Artifact: `artifacts/summary-skip-dogfood.log`.
