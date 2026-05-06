---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — hk2-plan-note

## What Changed

- Added `plan` to the HK note kind contract.
- Added `hk note --from-file PATH` for recording multi-line notes without forcing many serial CLI calls.
- Updated handoff rendering to include `Plan` and `Context` sections.
- Updated materialized views to include `plan.md` and `context.md`.
- Updated docs/spec to describe external planning translation as explicit plan/context/decision records, not heuristic CLI parsing.

## Why

- Planning often happens outside HK in chat, issues, or scratch docs, but the agreed result needs a durable place in the ledger before implementation/handoff.
- A fuzzy `hk adopt` parser would violate the no-heuristics direction; an explicit `plan` note lets the agent skill do interpretation while HK records the result.
- `--from-file` keeps the workflow compact and avoids turning plan adoption into many serial note/task commands.

## Where Reflected

- `src/harness_toolkit/kit/local.py`
- `src/harness_toolkit/kit/cli.py`
- `tests/unit/test_harness_kit_2.py`
- `docs/harness-kit-lifecycle-design.md`
- `docs/portable-workflow.md`
- `README.md`
- `SPEC.md`

## Promotion

- Contract is reflected in `SPEC.md` and docs. No ADR required; this is an incremental primitive under the ledger-first ADR.
