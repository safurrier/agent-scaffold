---
id: ci-hooks
title: CI & Hooks
description: >
  GitHub Actions workflow and pre-commit hook configuration. CI calls a single
  mise run ci entrypoint; hooks call the same mise tasks for guaranteed local parity.
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

The CI workflow is intentionally minimal — one entrypoint, no logic:

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
```

`mise-action` installs mise and runs `mise install` automatically, pulling tool versions from `.mise.toml`.

All quality gate logic lives in `mise run ci` → `mise run check`. The workflow is a thin wrapper.

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

This guarantees **CI parity**: if pre-commit passes, CI will pass. If CI fails, the hook would have caught it locally.

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

**Why not put logic in CI YAML?** Any logic in GitHub Actions YAML creates a split — developers run things differently locally than CI does. By having CI call `mise run ci` and pre-commit call `mise run <task>`, there is one source of truth for what "passing" means.

**Why `always_run: true`?** The tasks (`ruff`, `ty`, `pytest`) are fast enough that running them unconditionally is cheaper than filtering by changed files. It also prevents edge cases where a change to a config file doesn't trigger re-checking source files.
