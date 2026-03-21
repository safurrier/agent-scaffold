# Rust Stack

> **Status: IMPLEMENTED**

Tooling:
- fmt: `cargo fmt`
- lint: `cargo clippy --all-targets --all-features -- -D warnings`
- typecheck: `cargo check --all-targets --all-features`
- test: `cargo test --all-features`
- build: `cargo build --release`
- setup: `cargo fetch`

mise manages the Rust toolchain via `rust = "stable"` in `.mise.toml`.
