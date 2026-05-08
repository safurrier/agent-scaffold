---
id: plan-implementation
title: Implementation Plan
description: >
  Step-by-step approach for this unit of work.
  Optional — create only when the approach isn't obvious.
---

# Implementation — hk2-background-note-kind

## Approach

Make `background` the public note kind while keeping existing `context` events
renderable as historical aliases. This avoids a breaking display problem for any
local ledgers created during dogfooding without continuing to advertise
`context` as a valid new note kind.

## Steps

1. Replace `context` with `background` in valid note kinds and CLI choices.
2. Render `background` and historical `context` events under `## Background`.
3. Materialize `background.md`, including historical `context` events.
4. Update tests from context note assertions to background note assertions.
5. Update docs/spec command examples and explanation text.
6. Validate focused tests, full check, sync-check, and external review.
