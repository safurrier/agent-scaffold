---
id: plan-decisions
title: Decision Log
description: >
  Decisions made while implementing this unit of work.
---

# DECISIONS — hk-cli-help-idempotency-polish

## What Changed

- Root help now groups commands by primary lifecycle, guidance/discovery, evidence/review/handoff, and advanced/local state.
- Help examples are rendered as code blocks through a shared `examples()` helper.
- Advanced subcommands now have examples where they were missing.
- `hk start` now resumes the active same-slug work item instead of creating duplicate retry state.

## Why

- Agent-friendly CLIs should make the happy path obvious before exposing advanced surfaces.
- Agents copy examples from captured help; one-command-per-line examples are easier to reuse than densely wrapped prose.
- Agents retry commands after timeouts or uncertainty. A same-slug retry should not silently create duplicate lifecycle work.

## Where Reflected

- `src/harness_toolkit/kit/cli.py`
- `src/harness_toolkit/kit/app/lifecycle.py`
- `src/harness_toolkit/kit/local.py`
- `tests/unit/test_portable_workflow.py`
- `docs/agent-adoption.md`
- `docs/portable-workflow.md`

## Promotion

- Slice-local implementation decision. No new ADR needed; this is agent-friendly CLI polish under the existing lifecycle direction.
