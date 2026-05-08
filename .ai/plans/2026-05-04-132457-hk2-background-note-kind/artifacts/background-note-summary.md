# HK 2.0 Background Note Summary

## Purpose

Rename the public `context` note kind to `background` before the HK 2.0 note
contract settles.

## Changes

- Public note kinds now include `background` instead of `context`.
- `hk handoff` renders a `Background` section.
- `hk work materialize` writes `views/background.md`.
- Existing local ledger events with kind `context` are still displayed in the
  `Background` section and `background.md` view.
- Docs/spec/tests now describe `background` as stable facts, constraints,
  references, and framing needed for handoff.

## Rationale

`context` is overloaded in AI-agent workflows: context windows, context
engineering, context files, and general LLM context. `background` is more direct
for durable handoff facts and framing.
