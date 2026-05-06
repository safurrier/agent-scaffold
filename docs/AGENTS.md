# docs/ Index

Agent routing index for MkDocs-managed documentation. Structure is owned by `mkdocs.yml`.

## Tutorials

| Doc | Description |
|-----|-------------|
| `getting-started.md` | Install mise, clone, init a project interactively or non-interactively |

## How-to

| Doc | Description |
|-----|-------------|
| `development.md` | Contribute to the scaffold: test layers, fixtures, adding stacks |

## Explanation

| Doc | Description |
|-----|-------------|
| `index.md` | Project overview, design philosophy, quick start |
| `shapes.md` | Single-project vs apps workspace: layouts, workspace.toml, task behavior |
| `init-system.md` | How init transforms the scaffold: sequence, templates, cleanup |
| `ci.md` | CI workflow design: mise entrypoints, sync contract, pre-commit parity |
| `portable-workflow.md` | Attaching the planning workflow to existing repos without committed scaffold files |
| `harness-kit-lifecycle-design.md` | lifecycle-first local assistant design backed by ledger state |
| `script-contract-prototype.md` | Prototype for thin `scripts/*` adapter contract as a future scaffold task surface |

## Reference

| Doc | Description |
|-----|-------------|
| `task-contract.md` | Stable mise task contract, per-stack commands, speed tier |
| `release.md` | uv tool installation, GitHub tag release checklist, PyPI deferral |
| `stacks/index.md` | Stack comparison table, selection at init time |
| `stacks/acceptance-rubric.md` | Future stack acceptance bar and reviewer checklist |
| `stacks/python.md` | Python tooling: uv, ruff, ty, pytest configuration |
| `stacks/go.md` | Go tooling: gofumpt, golangci-lint, go test, Dockerfile |
| `stacks/rust.md` | Rust tooling: cargo fmt, clippy, check, test, Dockerfile |
| `decisions/0001-spec-driven-decision-loop.md` | SPEC.md, docs, and ADR loop |
| `decisions/0002-plan-workflow.md` | Plan directory workflow |
| `decisions/0003-deterministic-slice-contract.md` | Plan/spec/evidence/review contract |
| `decisions/0004-skill-first-slice-workflow.md` | Skill-first slice workflow |
| `decisions/0005-harden-sync-contract-ci.md` | Changed-plan sync-check CI mode |
| `decisions/0006-followup-contract-stack-rubric.md` | Slice workflow CLI and stack rubric |
| `decisions/0007-harness-toolkit-naming.md` | Harness Engineering Toolkit naming split: `hk`, `harness-kit`, `harness-scaffold` |
| `decisions/0008-harness-kit-ledger-first-local-assistant.md` | Initial lifecycle decision: local ledger, sync checkpoints, evidence capture |
| `decisions/0009-harness-kit-lifecycle-first-cli.md` | Lifecycle-first CLI decision that preserves handoff-safety guarantees |

<!-- generated-by: context-engineering@2.2.0 | last-updated: 2026-04-30 -->
