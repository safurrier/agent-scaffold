---
id: plan-implementation
title: Harness Kit Naming Implementation Plan
description: >
  Applied sequence for turning the naming brainstorm into repo changes.
---

# Implementation — harness-kit-naming

## Approach

Combine the naming capture and rename implementation into one slice because the
portable workflow CLI and scaffold/template names are the same product-boundary
decision.

The implementation performs a clean rename rather than maintaining legacy command
aliases:

```text
Umbrella/category:
  Harness Engineering Toolkit

Portable CLI/package:
  harness-kit
  CLI: hk
  readable alias: harness-kit

Starter template:
  harness-scaffold
  CLI: harness-scaffold
```

## Completed Steps

1. Renamed package/import surfaces from `agent_scaffold` to `harness_toolkit`.
2. Renamed console scripts to `harness-scaffold`, `harness-kit`, and `hk`.
3. Updated `.mise/tasks/init` to call `harness-scaffold init`.
4. Updated portable CLI copy, snippets, examples, and profile commands to use
   `hk` / `harness-kit`.
5. Updated docs and tests to reflect `harness-scaffold` as the starter template.
6. Added ADR 0007 to make the naming split durable.
7. Split the implementation package into `harness_toolkit.scaffold` and `harness_toolkit.kit` subtrees to match the product surfaces.
8. Add a shared names module for canonical commands and default profile paths.
9. Deepen profile loading/lookup/template operations behind a `ProfileCatalog` interface.

## Compatibility Policy

No legacy `agent-scaffold` or `agent-workflow` console scripts are registered in
this slice. Tests assert the old commands are absent so mixed command vocabulary
does not linger.

## Remaining Steps

1. Implement the package subtree split and `ProfileCatalog` refactor.
2. Run focused tests for CLI, profile, and contract behavior.
3. Run `mise run check`.
4. Run `mise run sync-check`.
5. Complete external review if preparing for merge/handoff.
