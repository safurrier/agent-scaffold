---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
---

# Specification — hk-profile-config-mvp

## Problem

HK2 now has a clear agent-facing lifecycle, but agents still need repo/module-specific operational knowledge: which focused checks to consider, what full gate exists, where to run commands, and what review backend is practical. Re-explaining this for every repo defeats the goal of using HK across many targets.

## User story

1. User maintains a local Harness Kit config with explicit target-to-profile bindings.
2. User gives an implementation agent a task and says to use `hk`.
3. Agent runs `hk profile resolve --target .` / `hk checks --target .` and sees the configured profile without heuristic auto-detection.
4. Agent runs native validation/review commands directly and records them with HK lifecycle evidence.

## Requirements

### MUST

- Add a user-level config file loaded by default from `$HARNESS_KIT_CONFIG` or `$XDG_CONFIG_HOME/harness-toolkit/harness.toml`, falling back to `~/.config/harness-toolkit/harness.toml`.
- Support inline profiles under `[profiles.<name>]` with `[[profiles.<name>.checks]]` using the existing profile/check schema: `title`, `summary`, `target_hint`, `instructions`, and per-check `name`, `purpose`, `command_template`, `run_from`, optional `required_inputs`, `notes`, and `agent_should_run_directly`.
- Support lightweight profile review guidance under `[[profiles.<name>.reviews]]` with `name`, `purpose`, `backend`, `rubric`, optional `dispatch_hint`, `prompt`, and `prompt_file`. Review definitions are guidance for agents to dispatch and then record with `hk review add`; HK does not launch them.
- Support explicit `[[targets]]` path bindings that map a target path to a profile.
- Add `hk profile resolve --target PATH --json` to report the matched profile, source, matched target, reason, and config path.
- Let `hk checks --target PATH` use the resolved profile when `--profile` is not explicitly supplied.
- Keep built-in profiles available and keep CLI `--profile` as the strongest explicit override.
- Keep profiles as guidance only: no auto-running, no confidence scoring, no heuristic command selection.
- Document user-level config and profile examples for harness-toolkit, dread, and foreman style repos.

### SHOULD

- Allow repo-level `.harness/harness.toml` as a future/optional layer if it stays simple and explicit.
- Show profile resolution in a way that agents can cite in status/handoff decisions.
- Keep the schema compatible with later splitting inline profiles into separate files.

## Constraints

- Do not silently ignore sync paths from config; known local state can only guide explicit `hk sync --exclude` usage.
- Do not implement `hk run` or automatic validation execution.
- Do not require committed `.harness/` for existing repos.
- Dogfood in temp clones only.
