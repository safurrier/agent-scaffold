---
id: plan-spec
title: Scope Specification
description: >
  Slice-local scope and acceptance criteria for HK 2.0 dogfood-driven UX fixes.
---

# SPEC — hk2-dogfood-ux-fixes

## Problem

PR-sized dogfood showed HK 2.0 is useful when agents discover it naturally, but
several sharp edges still cause wasted motion or incomplete lifecycle records:

- Current-checkout dogfood uses a wrapper because the installed `hk` is stale;
  that wrapper changes cwd semantics and makes `--target .` confusing.
- Workers repeatedly try bare command groups such as `hk evidence` and expect a
  useful default.
- Legacy commands such as `hk sync-check` still attract agents during lifecycle
  onboarding and produce old-workflow errors.
- Agents discover `plan`, `decide`, and review readiness late through `hk ready`
  failures rather than through a clear lifecycle path.
- Failed validation evidence renders as if it validates something rather than as
  an attempted validation.
- Agent-local state such as `.pi/` can stale sync unexpectedly.
- `hk context` is under-discovered on PR-sized tasks.
- The PR-sized dogfood replay process itself is valuable and should be captured
  as an in-repo development skill.

## Goals

1. Persist the PR-sized dogfood replay workflow as an in-repo agent skill.
2. Improve current-HK development/dogfood invocation so agents can run the right
   command surface without target confusion.
3. Make commonly guessed command-group invocations agent-friendly.
4. De-emphasize or clearly route legacy commands during HK 2.0 onboarding.
5. Improve lifecycle guidance so agents see the minimum readiness path early.
6. Fix handoff wording for failed evidence.
7. Decide how HK should handle common local agent state in sync freshness.
8. Keep HK shell-first: do not introduce `hk run` or make HK choose validation
   commands automatically.

## Non-goals

- Completing the profile versus `.harness/harness.toml` design.
- Implementing a full `hk finish`/`hk close` workflow unless explicitly selected.
- Making HK infer context or parse prior conversations.
- Solving Discord/Coder environment validation constraints.
- Merging worker code from dogfood trials.

## Proposed acceptance criteria

- A repo-local skill documents the PR-sized dogfood replay method, including
  shallow/temp snapshots, minimal prompting, HK command logging, worker reports,
  and synthesis.
- Agents have a documented/current dev invocation that preserves target semantics
  or makes absolute `--target` unavoidable.
- `hk evidence` either defaults to `list` or gives a direct next-command hint.
- Legacy lifecycle-confusing commands are less prominent in root help or clearly
  labeled as legacy.
- `hk start`, `hk ready`, and/or root help show the readiness loop:
  `start → context? → plan → decide → validate → review → sync → ready → handoff`.
- Handoff rendering distinguishes failed evidence as attempted validation.
- Sync freshness behavior around `.pi/`/agent-local state is intentional and
  documented/implemented according to the chosen policy.
- Unit tests cover any changed CLI behavior.
- `mise run check` and `mise run sync-check` pass before handoff.
