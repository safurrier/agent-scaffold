# agent-scaffold

Opinionated starter repository for agent-driven engineering. Provides a **stable task contract** via mise so AI-native codebases are deterministic, reproducible, and easy to validate. Clone it, run `mise run init`, and it transforms itself into your project.

## Repository Map

```
agent-scaffold/
├── .mise.toml                  # Tool versions + env vars (stack, shape, name)
├── .mise/tasks/                # 13 file-based task scripts (the contract)
├── .agent/skills/              # Agent skills (spec-sync, plan-sync, etc.)
├── .ai/plans/                  # Plan directories for units of work
├── scripts/
│   └── lib.py                  # Shared helpers (stack dispatch, module iteration)
├── stacks/                     # Per-stack template files (removed after init)
│   ├── python/                 # Python stack templates (.tmpl + source)
│   ├── go/                     # Go stack templates
│   ├── rust/                   # Rust stack templates
│   └── web/                    # Web/TS stack templates
├── templates/                  # Shared templates: README, CLAUDE.md, .gitignore
│   ├── .agent/skills/          # Skills shipped to generated repos
│   └── .ai/plans/              # Plan templates + example for generated repos
├── src/agent_scaffold/         # CLI package (click-based)
├── tests/                      # Scaffold self-tests
│   ├── contract/               # Structural checks (fast, no subprocess)
│   ├── unit/                   # Pure function tests (fast)
│   └── e2e/                    # Full init+setup+check workflows (slow)
├── docs/                       # MkDocs documentation source
├── SPEC.md                     # Correctness envelope (requirements, contracts, invariants)
└── pyproject.toml              # Package config + ruff/pytest/ty settings
```

### Key steering files

- `AGENTS.md` -- this file
- `SPEC.md` -- correctness envelope (requirements, contracts, invariants)
- `.mise.toml` -- tool versions, project env vars (`SCAFFOLD_PROJECT_*`)
- `mkdocs.yml` -- docs site navigation and theme

## How to Work Here

1. **Explore**: `mise tasks` lists all available commands
2. **Validate**: `mise run check` runs fmt-check + lint + typecheck + test
3. **Test fast**: `uv run pytest -m "not slow"` skips Go E2E tests
4. **Docs**: `mise run docs` starts the MkDocs dev server

## Common Commands

```bash
mise install                    # install tool versions from .mise.toml ✅
mise run setup                  # uv sync --all-extras ✅
mise run check                  # fast quality gate (fmt-check + lint + typecheck + test) ✅
mise run fmt                    # auto-format ✅
mise run lint                   # ruff check ✅
mise run typecheck              # ty check ⏸️ (may produce warnings on active codebase)
mise run test                   # pytest (parallel via xdist) ⏸️ (E2E tests need temp dirs)
mise run docs                   # MkDocs dev server at localhost:8000 ⏸️ (long-running)
mise run plan -- <slug>         # create a plan directory for a unit of work ✅
mise run init                   # transform scaffold into a project (one-time) ⏸️ (destructive)
mise run verify                 # heavy validation (integration, docker) ⏸️ (slow, may need Docker)
```

## System Invariants

- **Stable 13-task contract**: Every `.mise/tasks/` script must exist, be executable, have a `# MISE description=` header, and use `#!/usr/bin/env -S uv run python` shebang. Violation causes: contract test failures, agents cannot rely on the command surface.
- **CI parity**: `mise run check` locally must match what CI runs (`mise run ci` delegates to `check`). Pre-commit hooks call the same tasks. Violation causes: green local / red CI divergence.
- **Golden path guarantee**: A freshly initialized project (`mise run init`) must pass `mise run check` out of the box. Violation causes: broken first-run experience for users and agents.
- **Stack dispatch via env**: Tasks read `SCAFFOLD_PROJECT_STACK` from `.mise.toml` to dispatch to the correct toolchain. Violation causes: tasks run wrong language tools.

## Gotchas

- **DO** run `uv run pytest -m "not slow"` for fast feedback. **NOT** `uv run pytest` (includes Go E2E). **BECAUSE** Go E2E tests require the Go toolchain and take significantly longer.
- **DO** run `mise run check` before committing. **NOT** individual tasks separately. **BECAUSE** `check` runs fmt-check + lint + typecheck + test in the correct order with fail-fast.
- **DO** edit `.mise/tasks/<task>` to change task behavior. **NOT** `.mise.toml` task definitions. **BECAUSE** tasks are file-based scripts in `.mise/tasks/`, not inline TOML definitions.
- **DO** add new stacks in `stacks/<name>/` with corresponding task dispatch functions. **NOT** by editing task scripts inline. **BECAUSE** stack dispatch uses `dispatch_stack()` / `dispatch_module()` in `scripts/lib.py`; each stack registers handler functions.

## Task-Specific Docs

### Cross-cutting docs in `docs/` (MkDocs-managed)

| Doc | Topic |
|-----|-------|
| `docs/index.md` | Project overview and quick start |
| `docs/getting-started.md` | Full install and init walkthrough |
| `docs/task-contract.md` | All 13 tasks: purpose, per-stack commands |
| `docs/shapes.md` | Single vs apps workspace shapes |
| `docs/init-system.md` | How init transforms the scaffold |
| `docs/ci.md` | GitHub Actions workflow and pre-commit hooks |
| `docs/development.md` | Contributing: test layers, fixtures, adding stacks |
| `docs/stacks/index.md` | Stack comparison and selection |
| `docs/stacks/python.md` | Python stack: ruff, ty, pytest, uv |
| `docs/stacks/go.md` | Go stack: gofumpt, golangci-lint, go test |

## Key References

- **Task contract**: `docs/task-contract.md`
- **mise config**: `.mise.toml`
- **CI workflow**: `.github/workflows/ci.yml`
- **Init logic**: `src/agent_scaffold/` (CLI + init modules)
- **Design spec**: `SPEC.md`
