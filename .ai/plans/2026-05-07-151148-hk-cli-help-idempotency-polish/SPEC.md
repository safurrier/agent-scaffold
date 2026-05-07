---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
---

# Specification — hk-cli-help-idempotency-polish

## Problem

The previous agent-friendly CLI audit found four remaining polish gaps:

1. root help listed advanced commands next to primary lifecycle commands;
2. `hk start` was not retry-idempotent;
3. advanced subcommand examples were uneven;
4. Cyclopts rendered plain help examples densely in captured text.

## Requirements

### MUST

- Keep the promoted lifecycle visible as the first/root help path.
- Separate advanced/local commands from the primary lifecycle in root help.
- Make accidental same-slug `hk start` retries safe when the matching work item is already active.
- Do not duplicate plan/context notes on same-slug retry.
- Keep `hk start` capable of creating a new work item when the active work has a different slug.
- Add or normalize examples for advanced subcommands.
- Format examples so captured help keeps one command per line.
- Add focused tests for root help grouping and `hk start` retry behavior.

### SHOULD

- Document the retry behavior in agent-facing docs.
- Avoid a broad CLI redesign or new top-level commands.

## Constraints

- Preserve shell-first validation and existing lifecycle command names.
- Keep profile flags discovery-only; do not change the prior profile-flag fix.
- Do not make HK infer or execute validation commands automatically.
