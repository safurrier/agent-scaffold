---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for the portable workflow/profile DSL spike.
---

# Specification — portable-workflow-spike

## Problem

`hk` / `harness-kit` can create portable plan state, but it also needs to capture
the other thing harness-scaffold's `mise` contract provides: named verification
checks. For arbitrary repos, those checks are profile-specific and should be
discoverable by agents without turning `hk` into a task runner.

## Requirements

### MUST

- Provide built-in and explicit custom profile discovery for portable workflow usage.
- Represent profile checks as structured data: name, purpose, command template,
  cwd guidance, inputs, notes, and whether agents should run the command directly.
- Add CLI commands that expose profiles/checks/instructions without executing
  validation commands.
- Keep validation execution in the agent's normal shell loop so raw command output
  remains visible.
- Preserve explicit scope: agents pass `--target` and `--profile`; no config file
  or implicit profile inference is required.
- Keep target repositories clean in external and overlay modes.

### SHOULD

- Ship initial public `generic`, `python`, `go`, `rust`, and `rust-mise` profiles aligned
  with harness-scaffold's supported stacks and common task-runner contracts.
- Make all profile output available as JSON for agents.
- Keep help examples copyable.
- Keep the implementation type-safe with dataclasses and runtime validation for custom profile names.

## Constraints

- Do not add implicit user config files for this spike; custom profile catalogs must be passed explicitly with `--profiles-dir`.
- Do not implement `verify` or any validation-command execution wrapper.
- Do not require target repos to install mise or adopt harness-scaffold files.
- Do not encode guessed validation loops that cannot be supported by current repo
  context or existing skills.
