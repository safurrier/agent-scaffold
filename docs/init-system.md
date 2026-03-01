---
id: init-system
title: Init System
description: >
  How mise run init transforms the scaffold into a project: the full init sequence,
  template placeholder substitution, what gets removed, and validation rules.
index:
  - id: what-it-does
    keywords: [init-sequence, steps, transform, golden-path]
  - id: template-processing
    keywords: [placeholders, tmpl, project-name, module-name, go-module, authors-line]
  - id: what-gets-removed
    keywords: [cleanup, stacks, templates, spec-md, init-script]
  - id: non-interactive-mode
    keywords: [non-interactive, flags, name, shape, stack, modules, scripted]
  - id: validation
    keywords: [name-validation, regex, lowercase, hyphens, error]
---

# Init System

`mise run init` transforms the scaffold into your project. It runs once after cloning and then removes itself.

## What it does

```
1. Gather config (interactive prompts or --non-interactive flags)
2. Copy stack templates to project root (or apps/ modules)
3. Process .tmpl files — replace {{placeholders}} with project values
4. Rewrite .mise.toml with project name, shape, stack, and tool versions
5. Generate README.md and CLAUDE.md from templates
6. Generate .gitignore for the target stack
7. Generate workspace.toml (apps shape only)
8. Remove scaffold artifacts (stacks/, templates/, SPEC.md, init_project.py)
9. git init + initial commit
10. Install pre-commit hooks (unless --no-hooks)
11. mise run setup — install dependencies
12. mise run check — verify the golden path passes
```

The last step is the guarantee: **a freshly initialized project passes `mise run check` out of the box**.

## Template processing

Files with the `.tmpl` extension are processed by replacing `{{placeholder}}` strings:

| Placeholder | Value |
|-------------|-------|
| `{{project_name}}` | Project name (e.g. `my-service`) |
| `{{module_name}}` | Python module name (`my_service`) |
| `{{project_description}}` | Project description |
| `{{project_stack}}` | `python` or `go` |
| `{{go_module}}` | Go module path (e.g. `github.com/org/my-service`) |
| `{{author_name}}` | Author name |
| `{{author_email}}` | Author email |
| `{{authors_line}}` | Full `authors = [...]` TOML line |

## What gets removed

After init, the following scaffold artifacts are deleted:

- `stacks/` — per-stack template files
- `templates/` — README, CLAUDE.md, .gitignore templates
- `SPEC.md` — this specification
- `scripts/init_project.py` — the init script itself

The scaffold's test suite (`tests/`, `pyproject.toml`) is only removed for non-Python stacks. For Python single projects, the test suite itself becomes the project's test suite.

## Stack templates

### Python

Copies from `stacks/python/`:

```
pyproject.toml.tmpl  →  pyproject.toml
src/__init__.py      →  <module>/__init__.py
src/example.py       →  <module>/example.py
tests/__init__.py    →  tests/__init__.py
tests/test_example.py →  tests/test_example.py
```

### Go

Copies from `stacks/go/`:

```
go.mod.tmpl              →  go.mod
cmd/main.go              →  cmd/main.go
internal/app/app.go      →  internal/app/app.go
internal/app/app_test.go →  internal/app/app_test.go
Dockerfile.tmpl          →  Dockerfile
.golangci.yml            →  .golangci.yml
```

## Apps workspace shape

For each module declared in the init prompt (`--modules api,worker`):

1. Creates `apps/<module>/` directory
2. Copies the stack template into it
3. Generates `workspace.toml` listing all modules
4. Runs setup and check per-module via `run_per_module`

## Non-interactive mode

All prompts can be supplied as flags. The `--non-interactive` flag is required to skip the interactive UI:

```bash
mise run init -- \
  --non-interactive \
  --name my-platform \
  --shape apps \
  --stack python \
  --modules api,worker,scheduler \
  --author-name "Alice Smith" \
  --author-email "alice@example.com" \
  --no-examples
```

Missing required flags (`--name`) cause an immediate non-zero exit with a clear error message.

## Validation

Project names must match `^[a-z][a-z0-9-]*$`:

- Lowercase letters, digits, hyphens
- Must start with a letter
- No spaces, underscores, dots, or uppercase

Invalid names fail immediately:
```
Error: name must match ^[a-z][a-z0-9-]* (got 'My Project')
```
