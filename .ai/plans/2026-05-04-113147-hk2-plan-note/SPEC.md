---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — hk2-plan-note

## Problem

HK 2.0 expects research and planning to often happen outside the CLI in a
human/AI conversation, issue, scratch doc, or existing plan. The current CLI can
record generic context notes, but it lacks a clear durable slot for "this is the
agreed plan we are now implementing." Context notes also were not rendered in
handoffs, so plan distillation could disappear from the review surface.

A fuzzy `hk adopt` command would put conversation interpretation into the CLI.
That should stay in agent guidance/skills. The CLI should only record explicit
facts supplied by the agent or human.

## Requirements

### MUST

- Support `hk note --kind plan` as a typed note for compact adopted plan or
  implementation intent.
- Support `hk note --from-file PATH` so an agent can record a multi-line plan
  summary without many serial note commands.
- Reject calls that pass both positional note text and `--from-file`.
- Render plan notes in `hk handoff`.
- Render context notes in `hk handoff` so externally gathered context is visible.
- Materialize plan and context views from the ledger.
- Update docs/spec so external planning translation is represented as explicit
  plan/context/decision notes, not heuristic CLI parsing.

### SHOULD

- Keep the workflow lightweight: plan notes are concise summaries, not mandatory
  microtask lists.
- Preserve existing note behavior for learning, decision, gap, context, and
  spec-impact kinds.

## Constraints

- Do not add a fuzzy conversation parser or `hk adopt` command.
- Do not add task/review/readiness commands in this slice.
- Do not make HK a task runner.
