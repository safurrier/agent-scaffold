---
id: development
title: Development Guide
description: >
  Guide to developing agent-scaffold itself: test layer architecture, fixture patterns,
  adding new stacks, updating tool versions, and running the docs server.
index:
  - id: test-suite
    keywords: [contract, unit, e2e, slow, markers, pytest, xdist]
  - id: e2e-test-fixtures
    keywords: [py-single-ready, go-single-ready, module-scoped, fixture, mut]
  - id: adding-a-new-stack
    keywords: [new-stack, templates, task-dispatch, init-script, stacks-dir]
  - id: updating-tool-versions
    keywords: [tool-versions, mise-toml, rewrite, pyproject-tmpl]
---

# Development

Contributing to the scaffold itself.

## Setup

```bash
git clone https://github.com/safurrier/agent-scaffold.git
cd agent-scaffold
mise install          # installs python + uv
mise run setup        # uv sync --all-extras
```

## Running the scaffold's own checks

The scaffold is a Python project with its own `pyproject.toml`, ruff config, ty config, and pytest suite.

```bash
mise run check        # fmt-check + lint + typecheck + all tests (~30s)
mise run fmt          # auto-format scripts/ and tests/
mise run lint         # ruff check
mise run typecheck    # ty check
mise run test         # pytest
```

## Test suite

Tests live in `tests/` organized into three layers:

```
tests/
├── conftest.py              # shared helpers: mise(), init_project(), scaffold_copy
├── contract/
│   └── test_task_contract.py    # @contract — structural checks (fast, no subprocess)
├── unit/
│   └── test_init_project.py     # @unit — pure function tests (fast)
└── e2e/
    ├── conftest.py              # module-scoped fixtures: py_single_ready, etc.
    ├── test_python.py           # @e2e — Python happy path + gate tests
    └── test_go.py               # @e2e @slow @go — Go tests (needs Go toolchain)
```

### Running subsets

```bash
uv run pytest -m "not slow"          # default: contract + unit + Python E2E (~30s)
uv run pytest -m contract            # structural checks only (instant)
uv run pytest -m unit                # unit tests only (instant)
uv run pytest -m "e2e and not slow"  # Python E2E only
uv run pytest                        # full suite including Go (slow, needs Go)
```

### Parallelism

Tests run in parallel via pytest-xdist (`-n auto --dist=loadfile`). The `loadfile` distribution keeps module-scoped fixtures (like `py_single_ready`) on the same worker so they're created only once per file.

### Contract tests

`tests/contract/test_task_contract.py` verifies the scaffold itself before any init:

- All 11 task files exist in `.mise/tasks/`
- Every task file is executable
- Every task file has a `# MISE description=` header
- Every task file uses `#!/usr/bin/env -S uv run python` shebang
- `scripts/lib.py` exists
- CI workflow calls `mise run ci`
- Pre-commit config calls `mise run` tasks

### E2E test fixtures

The expensive module-scoped fixtures (`py_single_ready`, `go_single_ready`) run a full `init + setup` cycle once per test module:

```python
@pytest.fixture(scope="module")
def py_single_ready(tmp_path_factory):
    """Initialized + set-up Python single project (module scope)."""
    dest = tmp_path_factory.mktemp("py-single") / "scaffold"
    shutil.copytree(SCAFFOLD_ROOT, dest, ignore=_COPY_IGNORE)
    _trust_mise(dest)
    init_project(dest, name="testpyapp", shape="single", stack="python")
    _trust_mise(dest)   # init rewrites .mise.toml — trust it again
    mise("setup", dest, timeout=180)
    return dest
```

Negative-path tests copy the ready project via `py_single_mut` (function-scoped) to get a mutable, isolated copy.

## Docs

```bash
mise run docs    # start local MkDocs dev server at http://127.0.0.1:8000
```

## Adding a new stack

1. **Templates**: Create `stacks/<name>/` with source files and `.tmpl` variants
2. **Task scripts**: Add `<task>_<name>(cwd)` functions to each `.mise/tasks/<task>` script and register them in the `dispatch_stack` / `dispatch_module` calls
3. **Init script**: Add the stack to `SUPPORTED_STACKS` in `scripts/init_project.py`, add prompts/handling in `gather_interactive()`, add template copying in `init_single()` / `init_apps()`
4. **Docs**: Add `docs/stacks/<name>.md` and link it from `docs/stacks/index.md`
5. **Tests**: Add `tests/e2e/test_<name>.py` with happy path and gate tests

## Updating tool versions

Tool versions are declared in two places:

| Location | Purpose |
|----------|---------|
| `.mise.toml` | Scaffold's own tools (Python, uv) |
| `scripts/init_project.py` `rewrite_mise_toml()` | Tools written into generated projects |

The Python stack template (`stacks/python/pyproject.toml.tmpl`) also pins tool versions for generated projects.
