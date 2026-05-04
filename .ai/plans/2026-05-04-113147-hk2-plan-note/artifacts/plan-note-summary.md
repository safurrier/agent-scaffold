# HK 2.0 Plan Note Summary

## Purpose

Record the small implementation change that bridges external human/AI planning
into HK ledger state without adding a fuzzy conversation parser.

## Changes

- Added `plan` as a supported `hk note --kind` value.
- Added `hk note --from-file PATH` so agents can record a multi-line plan summary
  without issuing many serial note/task commands.
- Updated `hk handoff` to render `Plan` and `Context` sections.
- Updated `hk work materialize` to write `views/plan.md` and `views/context.md`.
- Updated docs/spec to describe planning translation as explicit agent-authored
  plan/context/decision notes.

## Design boundary

Conversation interpretation belongs in agent guidance/skills. HK records the
explicit plan text it is given; it does not parse chat transcripts, infer plans,
or score readiness.
