---
id: harness-toolkit-overview
title: harness-toolkit
description: >
  Overview of the Harness Engineering Toolkit: Harness Kit for existing repos
  and harness-scaffold for new repos.
index:
  - id: what-it-is
    keywords: [scaffold, clone-and-init, task-contract, agent-native]
  - id: why-mise
    keywords: [mise, tool-versions, task-runner, unified]
  - id: quick-start
    keywords: [install, clone, init, setup]
  - id: supported-stacks
    keywords: [python, go, rust, web, stacks, status]
---

# harness-toolkit

**Harness Engineering Toolkit** for agent-ready repositories.

Use **`hk` / `harness-kit`** for portable planning, validation, and handoff workflow in existing repos. Use **`harness-scaffold`** to start a new repo with the workflow, docs, CI, and stack defaults already wired in.

## What it is

harness-scaffold is a **clone-and-init** template. You clone it, run `mise run init`, and it transforms itself into your project — removing scaffold scaffolding, applying your project name, and verifying the golden path passes before handing control over.

Every generated project ships with a **three-surface split**:

- **`SPEC.md`** — correctness envelope (requirements, contracts, invariants)
- **`AGENTS.md`** — how to work here (commands, repo map, workflow)
- **`docs/`** — routed durable docs with explanation/reference/tutorial/how-to structure

The key insight: agents (and humans) benefit from a **fixed command surface**. Regardless of language, repo shape, or tooling choices, every project initialized from this scaffold exposes the same stable task contract:

```bash
mise run fmt        # format
mise run lint       # lint
mise run typecheck  # type checking
mise run test       # unit tests
mise run check      # all of the above (fast gate)
mise run plan       # create a plan directory for a unit of work on a feature branch
mise run sync-check # verify the slice is fully planned, evidenced, and reviewed
mise run verify     # heavy validation (integration, docker, etc.)
```

## Why mise

[mise](https://mise.jdx.dev/) manages both **tool versions** (Python, Go, uv, gofumpt, golangci-lint) and **task definitions** in one config file. It replaces Makefiles, shell scripts, and per-language task runners with a unified interface that works the same locally and in CI.

## Quick start

```bash
# 1. Install mise (only prerequisite)
curl https://mise.run | sh

# 2. Clone
git clone https://github.com/safurrier/harness-toolkit.git my-project
cd my-project

# 3. Install tools
mise install

# 4. Initialize
mise run init
```

See [Getting Started](getting-started.md) for the full walkthrough.

## Supported stacks

| Stack  | Format         | Lint           | Typecheck   | Test       | Status      |
|--------|----------------|----------------|-------------|------------|-------------|
| Python | ruff format    | ruff check     | ty          | pytest     | ✅ Available |
| Go     | gofumpt        | golangci-lint  | go vet      | go test    | ✅ Available |
| Rust   | cargo fmt      | cargo clippy   | cargo check | cargo test | ✅ Available |
| Web    | prettier       | eslint         | tsc         | vitest     | 🔜 Planned  |
