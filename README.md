# agent-scaffold

Opinionated starter repository for agent-driven engineering. Provides a stable task
contract via [mise](https://mise.jdx.dev/) so AI-native codebases are deterministic,
reproducible, and easy to validate.

## Prerequisites

Only one tool needs to be on your `PATH` before anything else — mise handles the rest.

```bash
# macOS / Linux (curl)
curl https://mise.run | sh

# macOS (Homebrew)
brew install mise

# Windows (PowerShell)
winget install jdx.mise
```

Once mise is installed, `mise install` will pull down everything declared in `.mise.toml`
(currently Python and uv for the scaffold itself; stack-specific tooling after `init`).

## Getting Started

```bash
# 1. Clone
git clone https://github.com/safurrier/agent-scaffold.git my-project
cd my-project

# 2. Install tools (Python + uv via mise)
mise install

# 3. Initialize — interactive
mise run init

# 4. Or non-interactively
mise run init -- --non-interactive --name my-project --shape single --stack python
```

## Task Contract

Every agent-scaffold project exposes these commands:

| Command | Purpose |
|---------|---------|
| `mise run init` | Initialize scaffold into a project |
| `mise run setup` | Install dependencies |
| `mise run fmt` | Auto-format code |
| `mise run lint` | Lint checks (non-modifying) |
| `mise run typecheck` | Static type analysis |
| `mise run test` | Unit tests |
| `mise run build` | Build artifacts |
| `mise run check` | Fast quality gate |
| `mise run plan-check` | Validate the active plan and metadata |
| `mise run spec-check` | Validate decision promotion and reflected docs |
| `mise run evidence-check` | Validate declared evidence artifacts |
| `mise run review-check` | Validate external review artifacts |
| `mise run sync-check` | Aggregate handoff readiness checks |
| `mise run slice-plan` | Render the planner prompt for the active slice |
| `mise run slice-implement` | Render the implementer prompt for the active slice |
| `mise run slice-review` | Render the reviewer prompt for the active slice |
| `mise run slice-status` | Show active slice state; use `mise -q run slice-status -- --json` for automation |
| `mise run dev` | Local development |
| `mise run ci` | CI entrypoint (= check) |
| `mise run docs` | Documentation server |
| `mise run plan -- <slug>` | Create a plan directory on a feature branch |
| `mise run verify` | Heavy validation |

## Supported Stacks

| Stack | fmt | lint | typecheck | test |
|-------|-----|------|-----------|------|
| Python | ruff format | ruff check | ty | pytest |
| Go | gofumpt | golangci-lint | go vet | go test |
| Rust | cargo fmt | cargo clippy | cargo check | cargo test |
| Web (TS) | prettier | eslint | tsc --noEmit | vitest |

> Web is planned. Python, Go, and Rust ship with templates and task wiring.

## Repo Shapes

- **Single-project**: One language, conventional layout (`src/`, `tests/` or `cmd/`, `internal/`)
- **Apps workspace**: Multiple apps under `apps/`, shared packages under `packages/`, with an explicit `workspace.toml` module registry

## Design Principles

1. **Stable task contract** — same commands regardless of stack or shape
2. **Thin orchestration** — mise delegates to language-native tools
3. **Fast `check`, explicit `verify`** — `check` is deterministic and fast; `verify` is heavier
4. **Deterministic CI** — GitHub Actions calls `mise run ci` and nothing else
5. **Deterministic slice handoff** — `sync-check` keeps plan/spec/evidence/review in lockstep
6. **CI parity** — pre-commit hooks call the same tasks as CI
