---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — portable-workflow-spike

## What Changed

- Added Cyclopts-backed `hk` / `harness-kit` commands for local/external workflow state: `instructions`, `profile list/show/create`, `checks`, `attach`, `plan`, `status`, and `sync-check`.
- Added a built-in profile/check DSL that describes named verification loops without executing them.
- Migrated `harness-scaffold init` and `hk` public CLI surfaces to Cyclopts and removed source/test Click usage.
- Removed `--module` from portable workflow scoping; `--target` now identifies the repo or scoped path and state is keyed by the target path relative to the git root.
- Added portable workflow docs describing external and overlay modes plus the minimal `AGENTS.md` snippet harnesses can read everywhere.
- Added unit coverage proving external state keeps a target repo clean, overlay mode uses `.git/info/exclude` instead of committed `.gitignore` changes, linked worktrees work, placeholder plans fail, and `attach --dry-run` does not write state.

## Why

- Shared repositories should be able to use Harness Kit's planning workflow without committing `.ai`, `.agent`, `.mise`, or `.gitignore` files.
- External state is safest for zero repo changes; overlay state is useful when agents/editors should see the workflow files in the checkout.
- Cyclopts gives the new agent-facing CLI typed signatures and Literal choices while preserving focused help output.
- A small `AGENTS.md` instruction is the right adoption surface: harnesses can read it once and apply the workflow in any repo they enter.
- Profiles preserve the useful part of the mise task contract — named loops like focused test, services, handoff — without turning `hk` into a subprocess task runner.
- A separate `--module` flag was pre-emptive; explicit target paths already express the intended scope and keep the CLI smaller.

## Where Reflected

- `src/harness_toolkit/kit/workflow.py`
- `src/harness_toolkit/kit/cli.py`
- `src/harness_toolkit/kit/profiles.py`
- `pyproject.toml`
- `uv.lock`
- `tests/unit/test_portable_workflow.py`
- `docs/portable-workflow.md`
- `mkdocs.yml`
- `docs/AGENTS.md`
- `AGENTS.md`

## Promotion

- Reflected in `docs/portable-workflow.md`; naming/product boundary is promoted in `docs/decisions/0007-harness-toolkit-naming.md`.
