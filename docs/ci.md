---
id: ci-hooks
title: CI & Hooks
description: >
  GitHub Actions workflow and pre-commit hook configuration. CI calls mise task
  entrypoints; hooks call the same tasks for guaranteed local parity.
index:
  - id: github-actions
    keywords: [workflow, ci-yml, mise-action, push, pull-request, two-tier]
  - id: pre-commit-hooks
    keywords: [pre-commit, hooks, fmt, lint, typecheck, test, install]
  - id: design-rationale
    keywords: [parity, always-run, single-source, logic-in-ci]
---

# CI & Hooks

## GitHub Actions

The CI workflow is intentionally thin: GitHub Actions installs tools and then
delegates validation to mise task entrypoints.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  check:
    name: Quality Gate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install mise
        uses: jdx/mise-action@v2
      - name: Setup
        run: mise run setup
      - name: Check
        run: mise run ci

  sync-check:
    name: Sync Contract
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install mise
        uses: jdx/mise-action@v2
      - name: Setup
        run: mise run setup
      - name: Sync check
        run: mise run sync-check
```

`mise-action` installs mise and runs `mise install` automatically, pulling tool versions from `.mise.toml`.

Quality gate logic lives in `mise run ci` → `mise run check`. Handoff contract
logic lives in `mise run sync-check`, which aggregates plan/spec/evidence/review
checks. The repository CI also runs generated-project smoke tests across the
supported stacks so Python, Go, and Rust scaffolds prove they can initialize and
pass `mise run check`.

## Pre-commit hooks

Pre-commit hooks mirror CI exactly — every hook calls a `mise run` task:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: fmt
        entry: mise run fmt
        language: system
        always_run: true
        pass_filenames: false

      - id: lint
        entry: mise run lint
        # ...

      - id: typecheck
        entry: mise run typecheck
        # ...

      - id: test
        entry: mise run test
        # ...
```

This guarantees **CI parity** for the fast quality gate: if pre-commit passes,
the `check` job should pass. `sync-check` remains the explicit handoff gate for
slice evidence and review completeness.

### Installing hooks

```bash
mise run setup   # installs hooks automatically if pre-commit is available
# or manually:
pre-commit install
```

### Running hooks manually

```bash
pre-commit run --all-files   # run all hooks on all files
pre-commit run fmt           # run a specific hook
```

## Design rationale

**Why not put logic in CI YAML?** Any logic in GitHub Actions YAML creates a split — developers run things differently locally than CI does. By having CI call `mise run ci`, `mise run sync-check`, and pre-commit call `mise run <task>`, there is one source of truth for what "passing" means.

**Why `always_run: true`?** The tasks (`ruff`, `ty`, `pytest`) are fast enough that running them unconditionally is cheaper than filtering by changed files. It also prevents edge cases where a change to a config file doesn't trigger re-checking source files.
