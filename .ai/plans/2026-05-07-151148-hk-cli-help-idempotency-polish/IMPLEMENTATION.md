---
id: plan-implementation
title: Implementation Notes
description: >
  What changed and where.
---

# IMPLEMENTATION — hk-cli-help-idempotency-polish

## Root help grouping

Updated `src/harness_toolkit/kit/cli.py` to define Cyclopts groups:

- `1. Primary lifecycle`
- `2. Guidance and discovery`
- `3. Evidence, review, and handoff`
- `4. Advanced/local state`

Top-level commands now render in those groups so the promoted lifecycle path appears first and advanced commands are no longer mixed into the same list.

## Help examples

Added an `examples()` helper that renders command examples as markdown code blocks. All existing help epilogues now use it, and advanced subcommands that lacked examples gained examples:

- `hk work start/status/materialize`
- `hk evidence list`
- `hk export`
- `hk spec init/status/outline/promote`

This keeps captured help text closer to one command per line instead of dense prose.

## `hk start` retry idempotency

Updated `LifecycleApp.start` so when the active work item was started with the same slug:

- it returns that active work item;
- JSON includes `resumed: true`;
- text output prints `resumed=true`;
- matching plan/context notes are not duplicated;
- missing or different plan/context text is added as normal lifecycle notes.

When the active work has a different slug, `hk start` keeps existing behavior and creates a new work item.

## Docs

Updated:

- `docs/agent-adoption.md`
- `docs/portable-workflow.md`

Both now mention that same-slug `hk start` retries resume active work instead of creating duplicate retry state.

## Tests

Added focused tests in `tests/unit/test_portable_workflow.py` for:

- root help grouping order;
- same-slug `hk start` retry resuming the existing work item;
- no duplicate plan note on retry.
