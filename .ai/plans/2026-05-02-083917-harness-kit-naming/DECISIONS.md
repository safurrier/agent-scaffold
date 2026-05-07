---
id: plan-decisions
title: Harness Kit Naming Decision Notes
description: >
  Slice-local decision staging area for the Harness Engineering Toolkit naming
  implementation.
---

# Decisions — harness-kit-naming

## What Changed

- Adopted **Harness Engineering Toolkit** as the umbrella/category name.
- Renamed the Python distribution to **`harness-toolkit`**.
- Renamed the import package to **`harness_toolkit`**.
- Renamed the starter-template command to **`harness-scaffold`**.
- Renamed the portable workflow CLI to **`hk`** with long alias
  **`harness-kit`**.
- Removed the old `agent-scaffold` and `agent-workflow` console scripts in this
  implementation because the project is still personal and cheap to rename.
- Kept the conceptual split:

  ```text
  Harness Engineering Toolkit
  ├── harness-kit / hk        # portable CLI/tooling layer
  └── harness-scaffold        # starter template for new projects
  ```

## Why

- `agent-workflow` is descriptive but generic and less memorable.
- `agent-harness` / `harness` fits the theme, but is confusing because Claude
  Code, Codex, Pi, Cursor, and similar tools are themselves coding harnesses.
- `hk` is short enough for frequent CLI use while `harness-kit` remains readable
  in docs and package metadata.
- Splitting the naming clarifies that one product helps existing repos adopt the
  workflow, while the scaffold/template creates new repos with the workflow built
  in.

## Where Reflected

- `pyproject.toml`
- `src/harness_toolkit/`
- `.mise/tasks/init`
- `README.md`
- `SPEC.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/getting-started.md`
- `docs/development.md`
- `docs/task-<REDACTED_TOKEN>.md`
- `docs/portable-workflow.md`
- `docs/decisions/0007-harness-toolkit-naming.md`
- `mkdocs.yml`
- `tests/`
- `.ai/plans/2026-05-02-083917-harness-kit-naming/artifacts/naming-brief.md`

## Promotion

- Promoted to ADR 0007: `docs/decisions/0007-harness-toolkit-naming.md`.
