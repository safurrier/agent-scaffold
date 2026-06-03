---
id: rust-stack
title: Rust Stack
description: >
  Rust stack tooling: cargo fmt for formatting, cargo clippy for linting,
  cargo check for type/borrow checking, cargo test for testing, and a
  multi-stage Dockerfile.
index:
  - id: tools
    keywords: [cargo, rustfmt, clippy, cargo-check, cargo-test, tools]
  - id: mise-tools
    keywords: [cargo-fmt, rustfmt, format]
  - id: task-commands
    keywords: [clippy, lint, warnings, deny, cargo-test]
  - id: project-structure-single
    keywords: [dockerfile, multi-stage, builder, runtime, bookworm]
  - id: test-results
    keywords: [cargo-test, test, all-features]
---

# Rust Stack

## Tools

| Purpose | Tool | Config |
|---------|------|--------|
| Formatter | [cargo fmt](https://github.com/rust-lang/rustfmt) | `rustfmt.toml` |
| Linter | [cargo clippy](https://github.com/rust-lang/rust-clippy) | (built into toolchain) |
| Type checker | cargo check | (built into toolchain, type + borrow analysis) |
| Test runner | cargo test | (built into toolchain) |
| Build | cargo build | (built into toolchain) |
| Docker | Multi-stage | `Dockerfile` (rust:slim → debian:bookworm-slim) |

## mise tools

The scaffold configures mise to manage the Rust toolchain:

```toml
[tools]
rust = "stable"
```

## Task commands

| Task | Command |
|------|---------|
| `mise run fmt` | `cargo fmt` (or `cargo fmt --check` with `--check` flag) |
| `mise run lint` | `cargo clippy --all-targets --all-features -- -D warnings` |
| `mise run typecheck` | `cargo check --all-targets --all-features` |
| `mise run test` | `cargo test --all-features` |
| `mise run build` | `cargo build --release` |
| `mise run setup` | `cargo fetch` |
| `mise run dev` | `cargo run` |

## Project structure (single)

```
my-project/
├── src/
│   ├── main.rs             # Entry point
│   └── lib.rs              # Library with examples
├── .mise.toml              # Task runner config
├── Cargo.toml              # Package manifest
├── rustfmt.toml            # Formatter config
├── Dockerfile              # Multi-stage build
└── README.md
```

## Test results

Generated CI captures cargo test output to a test-results file for artifact
upload, mirroring the Go stack's pattern.
