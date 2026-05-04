---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — hk2-background-note-kind

## Problem

The `context` note kind is too overloaded in AI tooling. It can be confused with
context windows, context engineering, repo context files, and general LLM context.
The intended note kind is simpler: stable background facts and framing that
should survive handoff.

## Requirements

### MUST

- Rename the public note kind from `context` to `background`.
- Render background notes under a `Background` handoff section.
- Materialize `views/background.md`.
- Preserve display compatibility for existing ledger events that were recorded
  with kind `context` by showing them in the `Background` section/view.
- Update tests, docs, and SPEC command examples.

### SHOULD

- Keep the valid note kind set small and avoid splitting `gap` into many variants
  yet.
- Keep `gap` wording, but render/describe it as gaps or follow-ups where useful.

## Constraints

- Do not add migration tooling for old local ledgers in this slice.
- Do not add new readiness/task/review commands.
