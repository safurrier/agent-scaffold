# harness-toolkit

**Harness Engineering Toolkit** for agent-ready repositories.

This package contains two related CLIs:

- **`hk` / `harness-kit`** — portable planning, validation, local work-ledger,
  command-evidence, sync-checkpoint, and handoff workflow for existing
  repositories without committing scaffold files.
- **`harness-scaffold`** — starter-template CLI for creating new agent-ready
  repositories with a stable task contract, docs structure, CI wiring, and slice
  workflow defaults.

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

## Install the CLIs

To use `hk` / `harness-kit` from any repository, install Harness Toolkit as a uv tool:

```bash
uv tool install git+https://github.com/safurrier/harness-toolkit.git
```

For a pinned GitHub release:

```bash
uv tool install git+https://github.com/safurrier/harness-toolkit.git@v0.1.0
```

For local development from a checkout:

```bash
uv tool install --editable ~/git_repositories/harness-toolkit
```

Verify:

```bash
hk --version
harness-kit --version
harness-scaffold --version
```

See [Release and Installation](docs/release.md) for release tags, upgrade commands,
and the current no-PyPI-yet policy. See [Harness Kit 2.0 Design](docs/harness-kit-2-design.md)
for the ledger-first local assistant migration direction.

To make Harness Kit the default workflow for your AI tools, add a compact
instruction block to your user-level `AGENTS.md` and point agents at a fuller
reference only when they are unfamiliar with the workflow. See
[Portable Workflow](docs/portable-workflow.md#user-level-agentsmd-bootstrap).

## Getting Started

```bash
# 1. Clone
git clone https://github.com/safurrier/harness-toolkit.git my-project
cd my-project

# 2. Install tools (Python + uv via mise)
mise install

# 3. Initialize — interactive
mise run init

# 4. Or non-interactively
mise run init -- --non-interactive --name my-project --shape single --stack python
```

## Harness Kit Workflow Modes

During the Harness Kit 2.0 migration, `hk` supports two related workflows:

- **Ledger-first local assistant** — use `hk brief`, `hk init`, `hk work start`,
  `hk note --kind plan`, `hk note`, `hk capture`, `hk sync`, and `hk handoff`
  for local agent memory, compact adopted plans, exact command evidence, sync
  freshness, and generated handoffs without committing ceremony.
- **Plan-artifact workflow** — use `hk plan`, `hk checks`, and `hk sync-check`
  when you need the existing durable plan package and handoff-readiness contract
  over TODO, decisions/spec impact, validation evidence, review records, and
  artifact manifests.

The intended lifecycle is `research → plan → implement → validate → review →
handoff`. Planning can happen outside HK in chat, issues, or scratch docs; agents
translate the agreed intent into compact HK plan/context/decision notes rather
than asking HK to infer it. Today, scaffolded plan artifacts represent that
lifecycle as Markdown/YAML files. The HK 2.0 direction is to make the ledger
canonical and materialize durable handoff views only when needed.

## Task Contract

Every project initialized from harness-scaffold exposes these commands:

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
