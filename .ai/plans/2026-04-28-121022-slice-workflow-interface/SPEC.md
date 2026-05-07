---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — slice-workflow-interface

## Problem

The deterministic slice contract branch has the right direction but the workflow
is split across low-depth phase skills, validation scripts, and docs. The
operator-facing shape should be clearer:

- skills own the workflow, judgment, rubrics, and prompt policy
- `mise` tasks own deterministic command entrypoints
- prompt rendering is provider-neutral and does not launch Codex, Claude, or an
  app-server in v1
- evidence and handoff files are durable, while raw transcripts, giant diffs,
  and scratch artifacts stay out of the durable repo context

This must build on the current stacked branch, including the Rust stack work.

## Requirements

### MUST

- Add a canonical slice workflow skill that explains planning, implementation,
  review, artifact policy, and holdout sample tasks.
- Keep `slice-planner`, `slice-implementer`, and `slice-reviewer` as thin
  compatibility entrypoints or replace them with an equivalent discoverable
  phase interface.
- Add deterministic `mise` task entrypoints for rendering phase prompts and
  reporting slice status.
- Keep v1 provider-neutral: render prompts to files/stdout; do not launch a
  coding harness.
- Include deterministic tests for new task files, prompt rendering, generated
  repo output, and Rust-stack generated repos.
- Update README, AGENTS, task-contract docs, SPEC/templates, and CI/task
  contract expectations so source and generated repos agree.
- Add holdout sample task fixtures or docs that can be used to evaluate prompt
  quality without blocking normal CI.
- Fix obvious docs drift from the Rust branch while touching the generated docs
  contract.

### SHOULD

- Prefer stdlib Python for task helpers so generated Go/Rust projects do not
  need extra Python dependencies to run workflow tasks.
- Avoid a public Python CLI for v1; if helper logic is needed, keep it behind
  the `mise` task surface.
- Use deterministic checks for CI blockers and keep fuzzy stale-doc or prompt
  quality checks as warnings/manual evals.

## Constraints

- Do not implement Symphony-style orchestration, issue polling, app-server
  sessions, background agents, or automatic harness launch.
- Do not make generated repos depend on a Python package install just to render
  prompts.
- Do not retain plan-local scratch artifacts as durable context unless they are
  intentionally summarized or declared.
