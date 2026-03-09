---
id: task-contract
title: Task Contract
description: >
  Reference for all 13 mise run tasks exposed by agent-scaffold projects: fmt, lint,
  typecheck, test, check, ci, verify, plan, and others. Same commands regardless of stack.
index:
  - id: contract-tasks
    keywords: [tasks, contract, stable, list, reference, plan]
  - id: check
    keywords: [check, quality-gate, fast, fmt-lint-typecheck-test]
  - id: verify
    keywords: [verify, heavy, integration, docker, slow]
  - id: ci
    keywords: [ci, entrypoint, github-actions]
---

# Task Contract

Every project initialized from agent-scaffold exposes these 13 tasks. The contract is **stable** — same command names regardless of stack or shape.

```bash
mise run <task>
```

## Contract tasks

| Task | Purpose | Speed |
|------|---------|-------|
| [`init`](#init) | Transform scaffold into a project | One-time |
| [`setup`](#setup) | Install deps, prepare environment | Fast |
| [`fmt`](#fmt) | Auto-format code | Fast |
| [`lint`](#lint) | Non-modifying lint checks | Fast |
| [`typecheck`](#typecheck) | Static type analysis | Fast |
| [`test`](#test) | Unit tests | Fast |
| [`build`](#build) | Produce artifacts | Medium |
| [`check`](#check) | fmt-check + lint + typecheck + test | Fast |
| [`dev`](#dev) | Start local development | Long-running |
| [`ci`](#ci) | CI entrypoint (= check) | Fast |
| [`docs`](#docs) | Documentation server | Long-running |
| [`plan`](#plan) | Create a plan directory | Fast |
| [`verify`](#verify) | Heavy validation | Slow |

---

## init

Transforms the scaffold into your project. Run once after cloning.

```bash
mise run init                                      # interactive
mise run init -- --non-interactive --name myapp    # scripted
```

See [Getting Started](getting-started.md) and [Init System](init-system.md).

---

## setup

Installs all project dependencies. Safe to re-run.

=== "Python"
    ```bash
    uv sync --all-extras
    ```

=== "Go"
    ```bash
    go mod download
    ```

For the apps workspace shape, `setup` iterates `workspace.toml` and runs the appropriate install per module.

---

## fmt

Auto-formats code in-place. Pass `--check` to fail without modifying (used by `check`).

=== "Python"
    ```bash
    uv run ruff format .          # format
    uv run ruff format --check .  # check only
    ```

=== "Go"
    ```bash
    gofumpt -w .   # format
    gofumpt -l .   # check only
    ```

```bash
mise run fmt           # format in-place
mise run fmt --check   # check only (used by CI)
```

---

## lint

Non-modifying lint checks. Fails on any violation.

=== "Python"
    ```bash
    uv run ruff check .
    ```

=== "Go"
    ```bash
    golangci-lint run ./...
    ```

---

## typecheck

Static type analysis.

=== "Python"
    ```bash
    uv run ty check
    ```

=== "Go"
    ```bash
    go vet ./...
    ```

!!! note "Go typecheck"
    Go's type system is enforced at compile time. `go vet` provides the closest equivalent to a standalone type-check pass.

---

## test

Unit tests only — no integration tests, no external services.

=== "Python"
    ```bash
    uv run pytest
    ```

=== "Go"
    ```bash
    CGO_ENABLED=0 go test ./...
    ```

---

## build

Produces distributable artifacts.

=== "Python"
    ```bash
    uv build
    ```

=== "Go"
    ```bash
    CGO_ENABLED=0 go build -o bin/ ./cmd/...
    ```

---

## check

**The primary quality gate.** Runs fmt (check mode), lint, typecheck, and test sequentially. Fails fast on the first error.

```bash
mise run check
```

This is what you run before every commit and what CI runs. It must be:

- **Fast** — deterministic, no network, no external services
- **Non-interactive** — safe in CI and pre-commit hooks
- **Comprehensive** — catches formatting, lint, type, and test failures

---

## dev

Starts local development. Long-running — stays in the foreground.

=== "Python"
    ```bash
    uv run python -m <module>   # requires __main__.py
    ```

=== "Go"
    ```bash
    go run ./cmd/...
    ```

For the apps workspace shape:
```bash
mise run dev -- api      # start the 'api' module
```

---

## ci

CI entrypoint. Currently an alias for `check`.

```bash
mise run ci
```

GitHub Actions calls exactly this — nothing else. All quality gate logic lives in `check` which `ci` delegates to.

---

## docs

Starts the MkDocs documentation server locally.

```bash
mise run docs    # serves at http://127.0.0.1:8000
```

---

## plan

Creates a plan directory for a new unit of work. Scaffolds META.yaml, TODO.md,
LEARNING_LOG.md, VALIDATION.md, and optional SPEC.md and IMPLEMENTATION.md.

```bash
git checkout -b feat/<slug>
mise run plan -- <slug>    # e.g., mise run plan -- add-user-auth
```

Creates `.ai/plans/YYYY-MM-DD-HHmmSS-<slug>/` with templates auto-filled (date,
branch). Refuses to run on the default branch. Slugs must be lowercase kebab-case
and unique within `.ai/plans/`.

See `.ai/plans/AGENTS.md` for the plan lifecycle and `_example/` for a reference.

---

## verify

Heavy validation that is **too slow for `check`**. Run before releases or on dedicated CI jobs.

Phases:

1. **check** — runs the full quality gate first
2. **Integration tests** — if `tests/integration/` exists
3. **Docker build** — if `Dockerfile` exists

```bash
mise run verify
```
