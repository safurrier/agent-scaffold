# agent-scaffold

## Commands

All commands use mise as the task runner:

- `mise run init` — Initialize scaffold into a project (interactive or --non-interactive)
- `mise run setup` — Install dependencies
- `mise run fmt` — Auto-format code
- `mise run lint` — Run linter (non-modifying)
- `mise run typecheck` — Static type analysis
- `mise run test` — Run unit tests
- `mise run build` — Build artifacts
- `mise run check` — Fast quality gate (fmt-check + lint + typecheck + test)
- `mise run ci` — CI entrypoint (= check)
- `mise run verify` — Heavy validation
- `mise run docs` — Serve documentation locally (MkDocs, scaffold-only)

## Testing the Scaffold

The scaffold ships with its own test suite (Python/pytest):

```bash
uv sync --all-extras          # install dev deps
uv run pytest -m "not slow"   # fast: contract + unit + Python E2E (~30s)
uv run pytest                 # full suite including Go E2E (slow, needs Go toolchain)
```

Test layers (in `tests/`):

- `contract/test_task_contract.py` — verify all 11 tasks exist and are executable (instant)
- `unit/test_init_project.py` — unit tests for `init_project.py` helper functions (instant)
- `e2e/test_python.py` — happy path + negative gate tests for Python stack (~22s)
- `e2e/test_go.py` — happy path + negative gate tests for Go stack (`@pytest.mark.slow`)

Marker shortcuts:

```bash
uv run pytest -m contract            # structural checks only
uv run pytest -m unit                # pure function tests only
uv run pytest -m "e2e and not slow"  # Python E2E only
```

## Architecture

- `.mise.toml` — Tool versions, project vars, env config
- `.mise/tasks/` — File-based task scripts (the contract implementation)
- `scripts/lib.py` — Shared Python helpers (stack dispatch, module iteration)
- `scripts/init_project.py` — Python init script
- `stacks/` — Per-stack template files (removed after init)
- `templates/` — Shared templates for README, CLAUDE.md, .gitignore (removed after init)
- `tests/` — Scaffold self-tests (removed after init for non-Python-single shapes)
- `docs/` — MkDocs documentation source

## Stack Dispatch

Tasks read `SCAFFOLD_PROJECT_STACK` from `.mise.toml` env and delegate to native tools.
For apps workspace shape, tasks iterate `workspace.toml` modules.

## Adding a New Stack

1. Add templates in `stacks/<name>/`
2. Add `<task>_<name>(cwd)` functions in each `.mise/tasks/<task>` script
3. Register in `dispatch_stack` / `dispatch_module` calls
4. Add the stack to `scripts/init_project.py` prompts and processing
5. Add `docs/stacks/<name>.md`
