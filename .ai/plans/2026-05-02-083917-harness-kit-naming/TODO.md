---
id: plan-todo
title: Harness Kit Naming Task List
description: >
  Checkable tasks for applying the Harness Engineering Toolkit naming split.
---

# TODO — harness-kit-naming

## Persisted direction

- [x] Capture the umbrella/product framing: Harness Engineering Toolkit.
- [x] Capture the portable CLI naming direction: `harness-kit` / `hk`.
- [x] Capture the starter-template rename: `harness-scaffold`.
- [x] Record why `agent-harness` / `harness` alone is ambiguous.

## Implementation

- [x] Rename the Python package metadata to `harness-toolkit`.
- [x] Move imports/package paths from `agent_scaffold` to `harness_toolkit`.
- [x] Expose `harness-scaffold` for template initialization.
- [x] Expose `hk` and `harness-kit` for the portable workflow CLI.
- [x] Remove old `agent-scaffold` and `agent-workflow` console scripts.
- [x] Update `.mise/tasks/init` to call `harness-scaffold`.
- [x] Update README, SPEC, docs, command examples, generated snippets, and tests.
- [x] Add ADR 0007 for the durable naming decision.
- [x] Run focused tests for scaffold CLI, portable workflow CLI, and task contract.
- [x] Split `harness_toolkit` into product subtrees: `scaffold/` and `kit/`.
- [x] Add canonical command-name constants so snippets/templates do not hand-write `hk` and `harness-scaffold` everywhere.
- [x] Deepen profile handling behind a `ProfileCatalog` interface.
- [x] Add inline architecture comments for future `kit_cli` and `workflow` seams.

## Handoff

- [ ] Run `mise run check` before handoff.
- [ ] Run `mise run sync-check` before handoff.
- [ ] Complete external review record if this slice is handed off for merge.
