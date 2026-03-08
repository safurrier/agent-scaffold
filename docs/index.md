---
id: agent-scaffold-overview
title: agent-scaffold
description: >
  Overview of agent-scaffold — an opinionated starter repo for agent-driven engineering
  that provides a stable mise task contract across Python and Go stacks.
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

# agent-scaffold

Opinionated starter repository for agent-driven engineering. Provides a **stable task contract** via [mise](https://mise.jdx.dev/) so AI-native codebases are deterministic, reproducible, and easy to validate.

## What it is

agent-scaffold is a **clone-and-init** template. You clone it, run `mise run init`, and it transforms itself into your project — removing scaffold scaffolding, applying your project name, and verifying the golden path passes before handing control over.

Every generated project ships with a **three-doc split**:

- **`SPEC.md`** — correctness envelope (requirements, contracts, invariants)
- **`AGENTS.md`** — how to work here (commands, repo map, workflow)
- **`docs/architecture.md`** — system description (principles, decisions, module map)

The key insight: agents (and humans) benefit from a **fixed command surface**. Regardless of language, repo shape, or tooling choices, every project initialized from this scaffold exposes the same 13 tasks:

```bash
mise run fmt        # format
mise run lint       # lint
mise run typecheck  # type checking
mise run test       # unit tests
mise run check      # all of the above (fast gate)
mise run verify     # heavy validation (integration, docker, etc.)
```

## Why mise

[mise](https://mise.jdx.dev/) manages both **tool versions** (Python, Go, uv, gofumpt, golangci-lint) and **task definitions** in one config file. It replaces Makefiles, shell scripts, and per-language task runners with a unified interface that works the same locally and in CI.

## Quick start

```bash
# 1. Install mise (only prerequisite)
curl https://mise.run | sh

# 2. Clone
git clone https://github.com/safurrier/agent-scaffold.git my-project
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
| Rust   | cargo fmt      | cargo clippy   | cargo check | cargo test | 🔜 Planned  |
| Web    | prettier       | eslint         | tsc         | vitest     | 🔜 Planned  |
