---
id: plan-decisions
title: Decisions
description: >
  Decision log for the slice.
---

# DECISIONS — hk-artifact-attach

## What Changed

- Added a generic `hk artifact attach` command instead of a session-specific transcript command.
- Attachments can be copied into HK local work artifacts or recorded by source path/hash only with `--no-copy`.
- Handoff rendering now includes an `Attached artifacts` section.

## Why

- The user wanted programmatic attachment of session/review transcripts without having the agent write its own prose transcript into HK.
- The generic artifact abstraction also covers Codex review transcripts, Pi session JSONL, browser HAR files, and raw validation artifacts.
- `--no-copy` is important for potentially sensitive or large agent session transcripts: HK can record file identity and hash without copying private contents into the work artifact directory.

## Where Reflected

- `src/harness_toolkit/kit/local.py`
- `src/harness_toolkit/kit/app/lifecycle.py`
- `src/harness_toolkit/kit/cli.py`
- `src/harness_toolkit/kit/ledger/store.py`
- `src/harness_toolkit/kit/rendering/handoff.py`
- `tests/unit/test_harness_kit_2.py`
- `tests/e2e/test_hk2_cli_parity.py`
- `tests/e2e/test_harness_kit_rollout.py`
- `README.md`
- `SPEC.md`
- `docs/portable-workflow.md`
- `docs/harness-kit-lifecycle-design.md`
- `AGENTS.md`

## Promotion

- No ADR; this is an incremental HK2 lifecycle capability captured in product docs and regression tests.
