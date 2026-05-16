# harness-toolkit

**Harness Engineering Toolkit** for agent-ready repositories.

Harness Toolkit has two related CLIs:

- **`hk` / `harness-kit`** — a portable lifecycle and readiness ledger for
  existing repositories. It records plan, context, validation evidence, review,
  sync state, and handoff output without forcing scaffold files into the repo.
- **`harness-scaffold`** — a starter-template CLI for creating new agent-ready
  repositories with a stable `mise` task contract, docs structure, CI wiring, and
  slice-workflow defaults.

Use `hk` when you already have a repo and want safer agent handoff. Use
`harness-scaffold` when you want a new repo to start with the same workflow and
command surface already installed.

## Install the CLIs

Harness Toolkit is currently distributed as a GitHub-sourced Python tool. PyPI is
intentionally deferred until the CLI contracts settle; prefer explicit GitHub
`main` or tag installs.

```bash
uv tool install git+https://github.com/safurrier/harness-toolkit.git
```

For a pinned release:

```bash
uv tool install git+https://github.com/safurrier/harness-toolkit.git@v0.2.0
```

For local development from a checkout:

```bash
uv tool install --editable ~/git_repositories/harness-toolkit
```

Verify the installed entrypoints:

```bash
hk --version
harness-kit --version
harness-scaffold --version
```

See [Release and Installation](docs/release.md) for upgrade commands, release
checklists, and the current no-PyPI-yet policy.

## Pick your path

### 1. Use `hk` in an existing repo

`hk` is for meaningful agent-driven changes: broad edits, risky work,
multi-step changes, or anything that may need context compaction or human
handoff. It is not a replacement task runner; keep running the repo's native
commands and let `hk` record what happened.

```bash
cd existing-repo
hk profile resolve --target . --json   # optional discovery
hk start demo-work --plan "Adopted implementation intent" --target .
# edit normally and run repo-native commands
hk checks --target . --changed --json   # suggests checks/reviews, does not run them
hk validate --why "Fast gate passes" --target . -- mise run check
hk status --target .
hk ready --target .
hk summary --target .
```

`hk status` is the coach. Agents should follow its next actions instead of
memorizing a long checklist. It will ask for missing context, plan updates,
decision/spec reflection, validation evidence, external-enough review, sync, or
an explicit dangerous skip when a lifecycle guarantee cannot be met.

To make this the default behavior for agents, add the compact directive from
[Agent Adoption](docs/agent-adoption.md) to your user-level or repo-level
`AGENTS.md`.

### 2. Create a new scaffolded repo

Only [mise](https://mise.jdx.dev/) needs to be on your `PATH`; it installs the
Python/uv tooling declared by the checkout and stack-specific tools after init.

```bash
# macOS / Linux
curl https://mise.run | sh

# or macOS with Homebrew
brew install mise
```

Then clone the scaffold and initialize it into your project:

```bash
git clone https://github.com/safurrier/harness-toolkit.git my-project
cd my-project
mise install
mise run init
```

For non-interactive setup:

```bash
mise run init -- \
  --non-interactive \
  --name my-project \
  --shape single \
  --stack python
```

After init, use the generated repo's stable task contract:

```bash
mise run setup
mise run check
mise run dev
```

See [Getting Started](docs/getting-started.md), [Task Contract](docs/task-contract.md),
[Repo Shapes](docs/shapes.md), and [Stacks](docs/stacks/index.md) for the full
scaffold reference.

### 3. Develop this checkout

This repo dogfoods Harness Kit for its own PR-sized work. Use repo-local guidance
from [AGENTS.md](AGENTS.md), then run the checkout's commands:

```bash
mise install
mise run setup
uv run pytest -m "not slow"   # focused iteration
mise run check                 # final fast gate
```

For meaningful Harness Toolkit changes, record the work with `hk`, validate with
repo-owned commands, get an external-enough review, then export a compact handoff
package when useful:

```bash
hk start demo-work --plan "Adopted implementation intent" --target .
hk validate --why "Fast gate passes" --target . -- mise run check
hk review prompt --target .
hk status --target .
hk ready --target .
```

Use `scripts/hk-dev ...` when you need to exercise this checkout's development
version of `hk` before the installed tool is updated.

## The lifecycle model

Harness Kit preserves a simple handoff-safety spine:

```text
plan → decision/spec reflection → validation evidence → external-enough review → readiness gate → handoff artifact
```

The readiness ledger is local state first. `hk` can render summaries, handoffs,
and exported packages, but it does not require existing repos to commit generated
ceremony. Scaffolded repos still keep the older slice-workflow task surface for
compatibility; `hk` and `harness-scaffold` remain separate on purpose.

Common `hk` actions:

| When you need to... | Use... |
|---|---|
| Start or inspect work | `hk start --plan ...`, `hk status`, `hk work status` |
| Record context, plan, or decisions | `hk context`, `hk plan`, `hk decide` |
| Capture command evidence | `hk validate --why "..." -- <native command>` |
| Add independent review | `hk review prompt`, then `hk review add` |
| Reconcile local state | `hk sync` or explicit `hk sync --exclude PATH --reason ...` |
| Check or share readiness | `hk ready`, `hk summary`, `hk handoff`, `hk export` |
| Make an explicit exception | `hk dangerously-skip review|validation|sync ...` |

Lower-level commands such as `hk note`, `hk evidence`, `hk capture`, and
`hk spec` are escape hatches, not the promoted path. See
[Harness Kit Design](docs/harness-kit-lifecycle-design.md),
[Profile Authoring](docs/profile-authoring.md), and
[Profile Reviews](docs/profile-reviews.md) for lifecycle and profile details.

## Scaffolded task contract, stacks, and shapes

Every project initialized from `harness-scaffold` gets the same task names, with
thin `mise` orchestration delegating to language-native tools:

| Workflow | Tasks |
|---|---|
| Setup and local loop | `setup`, `fmt`, `lint`, `typecheck`, `test`, `build`, `check`, `dev` |
| CI and heavier validation | `ci` (= `check`), `verify` |
| Slice handoff compatibility | `plan`, `plan-check`, `spec-check`, `evidence-check`, `review-check`, `sync-check`, `slice-plan`, `slice-implement`, `slice-review`, `slice-status` |

Supported scaffold stacks:

| Stack | Format | Lint | Typecheck | Test | Status |
|---|---|---|---|---|---|
| Python | `ruff format` | `ruff check` | `ty` | `pytest` | Available |
| Go | `gofumpt` | `golangci-lint` | `go vet` | `go test` | Available |
| Rust | `cargo fmt` | `cargo clippy` | `cargo check` | `cargo test` | Available |
| Web / TypeScript | `prettier` | `eslint` | `tsc --noEmit` | `vitest` | Planned |

Repo shapes are **single-project** and **apps workspace**. The full reference is
in [Task Contract](docs/task-contract.md), [Stacks](docs/stacks/index.md), and
[Repo Shapes](docs/shapes.md).

## Design principles

1. **Stable command surface** — agents and humans can rely on the same names
   across stacks and repo shapes.
2. **Thin orchestration** — `mise` task wrappers delegate to native tools instead
   of hiding the shell.
3. **Fast local gate, explicit heavy gate** — `mise run check` is the default;
   `mise run verify` is reserved for slower validation.
4. **Readiness over ceremony** — `hk` records enough plan, evidence, review, and
   sync state to make handoff honest without making existing repos adopt scaffold
   files.
5. **Explicit exceptions** — skipped validation, review, or sync must be recorded
   with scary, intentional `dangerously-skip` commands and mitigations.

## More docs

- [Getting Started](docs/getting-started.md) — scaffold walkthrough
- [Agent Adoption](docs/agent-adoption.md) — small `AGENTS.md` directive for agents
- [Harness Kit Design](docs/harness-kit-lifecycle-design.md) — lifecycle and ledger model
- [Task Contract](docs/task-contract.md) — full generated task reference
- [Development Guide](docs/development.md) — working on this checkout
- [Release and Installation](docs/release.md) — install, upgrade, and release policy
