---
id: agent-scaffold-spec
title: agent-scaffold Specification
description: >
  Correctness envelope for agent-scaffold — the requirements, contracts,
  and invariants that any valid implementation must satisfy.
index:
  - id: requirements
    keywords: [must, should, may, task-contract, init, check, ci, verify]
  - id: interfaces
    keywords: [cli, mise, tasks, stack-protocol, shapes, config]
  - id: invariants
    keywords: [ci-parity, golden-path, worktree, deterministic, stack-dispatch]
---

# agent-scaffold — Specification

> Correctness envelope for agent-scaffold. For how the system works now,
> see `docs/` (MkDocs site). For how to work in this repo, see `AGENTS.md`.

## Summary

agent-scaffold is an opinionated starter repository for agent-driven engineering. Clone it, run `mise run init`, and it transforms itself into a fully configured project with a stable 12-task command surface. Both humans and AI agents benefit from a language-agnostic, CI-parity contract where `mise run check` always works regardless of stack.

## Goals / Non-Goals

**Goals:**

- Provide a stable, minimal command surface for humans and agents
- Support two repo shapes: single-project and apps workspace
- Keep orchestration thin — delegate to language-native tools
- Make CI call the same entrypoints as local usage
- Preserve "batteries included" capabilities from reference templates (python-collab-template, go-template-project)

**Non-Goals:**

- No Bazel/Buck2 (v1)
- No implicit auto-discovery of apps based on folder existence — configuration is explicit
- No mandatory spec folder layout beyond the generated defaults
- No specific agent runtime requirement (Claude Code, Codex, Pi, etc.)

## Requirements

### MUST

- `mise run init` supports interactive and non-interactive modes
- `mise run init -- --non-interactive` with explicit flags produces deterministic output
- All 11 task scripts exist in `.mise/tasks/`, are executable, and have `# MISE description=` headers
- `mise run check` passes on a freshly initialized project without manual intervention (golden path)
- `mise run ci` produces identical results to `mise run check` (CI parity)
- Pre-commit hooks call the same tasks as CI
- Non-interactive init fails fast with clear errors on missing required inputs
- Generated projects include `AGENTS.md`, `SPEC.md`, `docs/architecture.md`, `docs/decisions/`, and CI workflow
- All generated docs have valid YAML frontmatter with `id`, `title`, `description`, and `index` fields
- ADRs have Status (from allowed values), Context, Decision, and Consequences sections

### SHOULD

- `mise run check` completes in under 60 seconds for a single-project repo
- Init prompts have sensible defaults for every field
- Generated docs have machine-readable frontmatter index entries with keywords
- Adding a new stack requires changes in one file (stack module) plus templates

### MAY

- Support additional stacks beyond Python and Go (Rust, Web/TS planned)
- Support `workspace.toml` module registry for apps-shape repos
- Support custom task scripts via plugin directories

## Interfaces & Contracts

**CLI:**

```
agent-scaffold init [OPTIONS]
  --non-interactive     Skip prompts, require all flags
  --name TEXT           Project name (required)
  --shape [single|apps] Repo shape (required)
  --stack [python|go]   Primary stack (required)
  --modules TEXT        Comma-separated module names (apps shape)
  --go-module TEXT      Go module path (Go stack)
  --no-hooks            Skip pre-commit hook installation
  --no-examples         Remove example code after init
```

**12-task contract:**

| Task | Purpose | Composition |
|------|---------|-------------|
| `init` | Transform scaffold into project | One-time, destructive |
| `setup` | Install dependencies | `uv sync` / `go mod download` |
| `fmt` | Auto-format | `ruff format` / `gofumpt` |
| `lint` | Lint check | `ruff check` / `golangci-lint` |
| `typecheck` | Type analysis | `ty check` / `go vet` |
| `test` | Unit tests | `pytest` / `go test` |
| `build` | Produce artifacts | Stack-dependent |
| `check` | Fast quality gate | fmt-check + lint + typecheck + test |
| `dev` | Local development | Stack-dependent |
| `ci` | CI entrypoint | Delegates to `check` |
| `docs` | Documentation server | MkDocs dev server |
| `verify` | Heavy validation | Integration, docker, security |

**Stack Protocol:**

```python
class Stack(Protocol):
    def init_single(self, root: Path, config: Config) -> dict[str, str]: ...
    def init_module(self, mod_dir: Path, config: Config, mod_name: str) -> dict[str, str]: ...
    def remove_examples(self, root: Path, config: Config) -> None: ...
    def remove_module_examples(self, mod_dir: Path) -> None: ...
    def tools_toml(self) -> str: ...
    def adr_notes(self) -> str: ...
    def stack_notes(self) -> str: ...
```

## Invariants

- **CI parity**: `mise run check` locally MUST match what CI runs. Pre-commit hooks call the same tasks. Violation causes green-local/red-CI divergence.
- **Golden path guarantee**: A freshly initialized project (`mise run init`) MUST pass `mise run check` out of the box. Violation breaks first-run experience.
- **Worktree safety**: All tasks must run from a clean checkout or Git worktree. No reliance on absolute paths, mutable global state, or undeclared local artifacts.
- **Stack dispatch via env**: Tasks read `SCAFFOLD_PROJECT_STACK` from `.mise.toml` to dispatch to the correct toolchain. Wrong dispatch = wrong tools run.
- **Deterministic output**: Non-interactive init with identical inputs produces identical output. Template rendering is deterministic.
- **stdlib-only test helpers**: `_docs_helpers.py` uses only stdlib (no pyyaml) so it's portable into generated repos without adding dependencies.

## Acceptance

```bash
mise run check          # fast: fmt-check + lint + typecheck + all tests
mise run verify         # heavy: integration, e2e, docker (when applicable)
```

Contract tests verify structural invariants (task files, doc schemas, template sections).
Golden output tests verify deterministic rendering across all 4 shapes (Python single/apps, Go single/apps).
E2E tests verify the full init → setup → check pipeline produces passing projects.
