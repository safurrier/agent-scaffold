---
id: plan-implementation
title: Implementation Plan
description: >
  Step-by-step plan for adding Harness Kit portable workflow state and profiles.
---

# Implementation — portable-workflow-spike

## Approach

Treat profiles as workflow contracts for agentic engineering checks. The profile
layer describes named verification checks and associated guidance; it does not
execute those checks. Agents discover the closest profile, run validation directly
with normal shell tooling, then record the command/result in the portable plan's
validation log.

The final naming split is:

- `hk` / `harness-kit` — portable workflow CLI for existing repos.
- `harness-scaffold` — starter-template CLI for new repos.
- `harness_toolkit` — Python import package that contains both surfaces.

## Steps

1. Add portable workflow state in `src/harness_toolkit/kit/workflow.py` with external
   and overlay modes.
2. Add profile dataclasses, built-in profiles, custom TOML loading, and
   `profile create` template generation.
3. Expose `hk` commands for profile discovery, checks, instructions, attach,
   plan, status, and sync-check.
4. Keep validation execution explicit and non-wrapped: agents run commands
   directly and record evidence.
5. Rename the package and public CLI surfaces to the Harness Engineering Toolkit
   naming (`harness-toolkit`, `harness_toolkit`, `harness-scaffold`, `hk`).
6. Add tests for profile discovery, JSON shape, custom profile loading,
   no-validation-execution, clean target repos, overlay ignores, CLI rename, and
   absence of legacy console scripts.
7. Update docs, ADR 0007, and plan evidence.
8. Run focused tests, contract/unit tests, `mise run check`, and `mise run
   sync-check`.
