---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — hk2-background-note-kind

## What Changed

- Replaced the public `context` note kind with `background`.
- Updated handoff output to render `## Background`.
- Updated materialized views to write `background.md`.
- Kept historical `context` ledger events visible by rendering them with background notes.
- Updated docs, spec, and tests to use `background`.

## Why

- `context` is too overloaded in AI-agent workflows and can be confused with context engineering, context files, and context windows.
- `background` more clearly describes stable facts, constraints, references, and framing needed for handoff.
- Backward-compatible rendering avoids losing local dogfood notes that were already recorded as `context`.

## Where Reflected

- `src/harness_toolkit/kit/local.py`
- `src/harness_toolkit/kit/cli.py`
- `tests/unit/test_harness_kit_2.py`
- `docs/harness-kit-2-design.md`
- `docs/portable-workflow.md`
- `docs/decisions/0008-harness-kit-2-ledger-first-local-assistant.md`
- `README.md`
- `SPEC.md`

## Promotion

- Contract reflected in `SPEC.md` and docs. No ADR required; this is a naming refinement under the ledger-first ADR.
