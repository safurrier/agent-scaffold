---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
---

# Specification — hk-agent-friendly-cli-polish

## Problem

The agent-adoption dogfood trial showed that a fresh agent followed the generated AGENTS.md snippet, but copied profile discovery flags onto `hk start`. Cyclopts rejected the command, and the agent recovered. The recovery is acceptable, but the error is avoidable and should be easier for agents to self-correct.

The user also asked for a quick Harness Kit CLI pass using the agent-friendly CLI checklist.

## Requirements

### MUST

- Keep profile flags scoped to discovery commands rather than adding no-op `--profile` behavior to lifecycle commands.
- Update generated instructions so agents know not to propagate `--profile` / `--profiles-dir` to lifecycle commands.
- Make accidental profile flags on lifecycle commands fail with an actionable error and repair hints.
- Preserve native command arguments after `hk validate --`; HK must not treat a native command's own `--profile` as an HK misuse.
- Add focused tests.
- Record an agent-friendly CLI audit with remaining gaps.

### SHOULD

- Improve examples on promoted or commonly coached subcommands when low-risk.
- Keep docs generic and public; do not add personal setup notes.

## Constraints

- Harness Kit remains shell-first. Do not turn profiles into automatic validation execution.
- Do not add profile flags to lifecycle commands unless they have semantics.
- Keep changes small enough for the current PR.
