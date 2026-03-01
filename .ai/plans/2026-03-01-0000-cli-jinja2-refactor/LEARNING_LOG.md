# Learning Log — CLI + Jinja2 Refactor

**Plan**: Decompose `scripts/init_project.py` into a Click CLI package, replace `{{}}` template engine with Jinja2, close Go apps test gap.

---

## Full Arc of Work

This was a multi-session effort. The first session built the scaffold from scratch and got it to 131 tests passing. The second session picked up the retrospective and did the refactor. Here's the full narrative.

### Session 1: Initial Build

Built the scaffold from zero: `.mise.toml`, task scripts, stack templates, contract/unit/E2E tests across Python single, Python apps, and (partly) Go shapes. Landed at 131 tests passing with `mise run check` green.

Key tests added near end of session 1:
- `test_claude_skills_symlink` — verify `.claude/skills → .agent/skills` symlink was created
- `test_agent_skills_exists` — verify `example-skill` is present in `.agent/skills/`
- `test_test_passes` — verify `junit.xml`/`go-test.txt` artifacts are produced after `mise run test`

### Session 2: Retrospective + Refactor Plan

**Grade assessment (B+)** identified gaps:
- `scripts/init_project.py` was a 400+ line procedural monolith — adding a new stack required touching 6 locations (shotgun surgery)
- Template engine was `{{}}` string substitution on raw file content — no conditionals, loops, undefined-variable errors
- No `TestGoAppsHappyPath` — Go apps shape had zero happy-path E2E coverage
- `tests/e2e/test_go.py` only had negative gate tests

**Design discussion**: User asked if `init_project.py` was a code smell. Two options surfaced:
- Option A: Module decomposition (still a library, split by concern)
- Option B: Click CLI tool (`uv run agent-scaffold init`)

User chose CLI because it creates a tool agents can use directly, not just Python code.

**Plan approved with one correction**: Initial plan proposed `BaseStack(ABC)`. User rejected: "I don't like ABCs I prefer protocols." Revised to `Stack(Protocol)` — plain classes, no inheritance required, structural subtyping.

**CLI skill lookup**: Before finalizing, pulled conventions from `../dots` python-cli skill:
- `click.secho()` with `fg=` for colored output, `err=True` for stderr
- `click.ClickException` for user-facing errors — never expose tracebacks
- `CliRunner` with `isolated_filesystem()` and `input=` parameter for unit tests
- `--debug/--no-debug` flag + `AGENT_SCAFFOLD_DEBUG` envvar for opt-in tracebacks

---

## What Was Built

### New package: `src/agent_scaffold/`

| Module | Purpose |
|--------|---------|
| `cli.py` | Click group + `init` command, argument validation, MISE_PROJECT_ROOT detection |
| `config.py` | `Config` dataclass, `validate_name()`, `to_module_name()`, constants |
| `templates.py` | Jinja2 engine: `render_template()`, `render_string()`, `copy_tree()` |
| `stacks/base.py` | `Stack` Protocol (structural interface) |
| `stacks/python.py` | `PythonStack` — single + apps shapes |
| `stacks/go.py` | `GoStack` — single + apps shapes |
| `stacks/__init__.py` | Registry: `STACKS = {"python": PythonStack(), "go": GoStack()}` |
| `common.py` | `run_init()` orchestrator, `cleanup_scaffold()`, `generate_docs()`, `git_init()` |
| `prompts.py` | `gather_interactive()` using `click.prompt()` |

### Templates upgraded

- `workspace.toml.tmpl`: `{{module_entries}}` (string blob) → Jinja2 `{% for name, info in modules.items() %}` loop
- `pyproject.toml.tmpl`: `{{authors_line}}` (computed by Python) → Jinja2 `{% if author_name and author_email %}` conditional
- `stacks/python/src/__init__.py` → renamed to `.tmpl` (had `{{project_name}}`)
- `stacks/python/tests/test_example.py` → renamed to `.tmpl` (had `{{module_name}}`)
- `stacks/go/cmd/main.go` → renamed to `.tmpl` (had `{{project_name}}`)

### Wiring changes

- `.mise/tasks/init` now delegates to `uv run agent-scaffold init` via `subprocess.run`
- `pyproject.toml`: added `click>=8.0`, `jinja2>=3.0`; added entry point `agent-scaffold = "agent_scaffold.cli:cli"`; moved from `scripts/` to `src/` layout
- `scripts/init_project.py` deleted
- Stack shotgun-surgery cost: was 6 locations, now 1 file per new stack

### New tests

- `tests/unit/test_templates_jinja.py` (10 tests): render, conditionals, loops, StrictUndefined, trailing newline, copy_tree with .tmpl stripping, binary file passthrough
- `tests/unit/stacks/test_python.py` (3): tools_toml, adr_notes, stack_notes
- `tests/unit/stacks/test_go.py` (3): tools_toml, adr_notes, stack_notes
- `tests/unit/test_cli.py` (7): help output, non-interactive missing-flag errors, invalid name/shape/stack rejection
- `tests/e2e/test_go.py::TestGoAppsHappyPath` (3): init_succeeds, workspace_toml_lists_modules, check_passes
- Contract: `test_cli_package_exists` + `test_cli_entry_point_registered` (replaced `test_init_script_exists`)

---

## What Diverged

### Template extension gap (not anticipated)

The old `{{}}` engine applied substitution to **every file** in the stacks directory. The new `copy_tree()` only renders `.tmpl` files. Three files had template variables but no `.tmpl` extension — they were copied verbatim into generated projects, causing ruff parse errors (`Expected a module name`) on lines like `from {{module_name}}.example import Greeter`.

**Lesson**: When migrating from "render everything" to opt-in `.tmpl`, run `grep -rl '{{' stacks/` before writing any code — surfaces the gap in 2 seconds.

### Lint errors caught post-implementation

1. **B904** — `raise click.ClickException(str(e))` inside `except` needs `from e`. Not covered by `python-cli` skill examples.
2. **UP037** — `"Config"` quoted annotation in Protocol body was redundant given `from __future__ import annotations` at module top. Ruff auto-fix candidate, but still cost a round-trip.

Both were quick fixes. Running `mise run check` (not just `pytest`) earlier in the TDD cycle would have caught these before the "done" declaration.

### Plan artifact directory never created

The plan was approved at the very end of a session that hit context limit. `.ai/plans/` was never written during plan mode. This LEARNING_LOG is a retrospective reconstruction.

---

## What Would Enable One-Shot Execution Next Time

1. **Pre-migration audit**: `grep -rl '{{' stacks/` as the first step of any template engine migration
2. **`mise run check` during TDD**: run after each implementation batch, not just at the final gate
3. **Create `.ai/plans/<slug>/` at plan approval time**: even a stub SPEC.md anchors context across sessions and survives context resets
4. **`Stack` Protocol boundary test**: a small test asserting `PythonStack()` satisfies `Stack` (via `runtime_checkable`) would catch Protocol drift without reading the source

---

## Skill Usefulness

| Skill | Usefulness | Notes |
|-------|-----------|-------|
| `python-cli` | High | `CliRunner`, `ClickException`, `click.secho` applied directly; missing B904 chained-raise pattern |
| `testing-pytest` | High | Module-scope fixture for `go_apps_ready`, `isolated_filesystem()` for CLI tests |
| `python-core` | High | Protocol > ABC — zero boilerplate, structural subtyping just works |
| `testing-core` | Medium | TDD order held; unit tests kept narrow (argument validation only, not full init) |
| `development-debugging` | Low | No complex debugging needed this session |

---

## Final Numbers

| Metric | Before | After |
|--------|--------|-------|
| Tests | 131 | 155 |
| `init_project.py` lines | ~400 | 0 (deleted) |
| Template files with `{{}}` but no `.tmpl` | 3 (bug) | 0 |
| Stack addition cost | 6 locations | 1 file |
| New package modules | 0 | 9 |
| Jinja2 templates with control flow | 0 | 2 |
