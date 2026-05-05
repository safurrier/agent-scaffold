---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — hk2-dogfood-ux-fixes

## What Changed

- Planned a follow-up implementation slice from PR-sized dogfood findings.
- Promoted the PR-sized dogfood replay process itself to a durable in-repo skill.
- Captured user decisions for the first implementation pass.

## Why

- The dogfood workflow generated high-signal findings and should be reusable by
  future agents without rediscovering the setup.
- Several fixes involve product tradeoffs, not just code edits: command aliases,
  legacy command visibility, sync freshness semantics, and current-HK dev
  invocation.

## Decisions from questionnaire

### Persist dogfood as repo-local skill only

Decision: Add an in-repo development skill under `.agent/skills/`, not generated
templates yet.

Why: The workflow is useful for harness-toolkit development, but it is still an
internal/product dogfood process. Avoid exporting it to every scaffolded repo
until it hardens.

### Add a current-HK dev shim/task

Decision: Add a repo task or dev shim for running the current checkout's HK
command surface without the `uv --directory` cwd/target surprise.

Why: The stale globally installed `hk` and ad-hoc wrapper caused real target
confusion. Dogfood should exercise current HK without requiring agents to use an
unsafe wrapper.

### Bare `hk evidence` should fail with a direct hint

Decision: Keep command groups explicit, but make bare `hk evidence` fail with an
actionable hint such as `Try: hk evidence list --target ...`.

Why: Agents repeatedly guessed `hk evidence`; a direct hint preserves CLI
strictness while eliminating dead-end errors.

### Move/hide legacy commands under `hk legacy`

Decision: De-emphasize root-level legacy commands like `sync-check` and route
agents through `hk legacy` for HK 1.x plan-artifact workflows.

Why: Lifecycle-first HK 2.0 should present one obvious path. Legacy commands in
root help caused agents to drift into old workflow errors.

### Treat agent-local sync state carefully, not silently

Decision: Do not silently ignore `.pi/`/agent-local state as a first move. Add a
warning/diagnostic path now, and design an explicit override/ignore mechanism as
a follow-up if needed.

Why: Sync freshness should remain trustworthy. If HK excludes paths, users need a
visible contract such as a harness ignore file or a scary override, not hidden
magic.

### Strengthen optional context guidance

Decision: Update start/root guidance to make `hk context` more discoverable for
PR-sized constraints, relevant files, environment blockers, and repo facts, while
keeping it optional.

Why: Workers never used context on PR-sized tasks. The command should be easier
to discover without turning context into ceremony.

### Defer finish/close helper

Decision: Do not add `hk finish`/`hk close` in this slice.

Why: Fix discoverability and command-shape issues first. A finalization helper can
come later if stale final states remain common.

## Where Reflected

- `.ai/plans/2026-05-05-072708-hk2-dogfood-ux-fixes/SPEC.md`
- `.ai/plans/2026-05-05-072708-hk2-dogfood-ux-fixes/TODO.md`

## Promotion

- Ready for implementation planning.
