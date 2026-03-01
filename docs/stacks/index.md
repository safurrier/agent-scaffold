---
id: stacks-overview
title: Stacks
description: >
  Overview of supported language stacks (Python, Go) and planned stacks (Rust, Web),
  with a per-stack tool comparison table and how to select a stack at init time.
index:
  - id: stack-comparison
    keywords: [python, go, rust, web, fmt, lint, typecheck, test, comparison]
  - id: stack-selection
    keywords: [select, init, scaffold-project-stack, env-var]
---

# Stacks

A **stack** is the set of language-native tools wired into the task contract. Every task delegates to its stack's tools.

## Stack comparison

| | Python | Go | Rust | Web (TS) |
|--|--------|-----|------|----------|
| **Status** | ✅ Available | ✅ Available | 🔜 Planned | 🔜 Planned |
| **fmt** | ruff format | gofumpt | cargo fmt | prettier |
| **lint** | ruff check | golangci-lint | cargo clippy | eslint |
| **typecheck** | ty | go vet | cargo check | tsc --noEmit |
| **test** | pytest | go test | cargo test | vitest |
| **build** | uv build | go build | cargo build --release | vite build |
| **Tool manager** | uv | go toolchain | cargo | npm/pnpm |

## Stack selection

Set at `init` time via `--stack`:

```bash
mise run init -- --non-interactive --name myapp --stack python
mise run init -- --non-interactive --name myservice --stack go
```

After init, the stack is recorded in `.mise.toml`:

```toml
[env]
SCAFFOLD_PROJECT_STACK = "python"
```

All task scripts read this variable to dispatch to the correct toolchain.

## Detailed docs

- [Python stack](python.md)
- [Go stack](go.md)
