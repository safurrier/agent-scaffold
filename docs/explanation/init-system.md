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
5. Generate SPEC.md, README.md, AGENTS.md (+ CLAUDE.md symlink) from templates
6. Generate the routed docs tree, including architecture, decision ledger, ADR seed, and review rubrics
7. Generate .agent/skills/ (+ .claude/skills symlink) from templates
8. Generate .github/workflows/ci.yml from template
9. Generate .gitignore for the target stack
10. Generate workspace.toml (apps shape only)
11. Remove scaffold artifacts (stacks/, templates/, scaffold docs/, src/)
12. git init + initial commit
13. Install pre-commit hooks (unless --no-hooks)
14. mise run setup — install dependencies
15. mise run check — verify the golden path passes
```

The last step is the guarantee: **a freshly initialized project passes `mise run check` out of the box**.

## Template processing

Files with the `.tmpl` extension are processed by replacing `{{placeholder}}` strings:

| Placeholder | Value |
|-------------|-------|
| `{{project_name}}` | Project name (e.g. `my-service`) |
| `{{module_name}}` | Python module name (`my_service`) |
| `{{project_description}}` | Project description |
| `{{project_stack}}` | `python`, `go`, `rust`, or `web` |
| `{{go_module}}` | Go module path, for example github.com/org/my-service |
| `{{author_name}}` | Author name |
| `{{author_email}}` | Author email |
| `{{authors_line}}` | Full `authors = [...]` TOML line |

## What gets removed

After init, the following scaffold artifacts are deleted:

- `stacks/` — per-stack template files
- `templates/` — shared template files
- `src/` — scaffold CLI package
- `docs/` — scaffold's MkDocs site (replaced with generated project docs)
- `mkdocs.yml` — scaffold's MkDocs config
- legacy init script, if present

The scaffold's Python package config (`pyproject.toml`) is removed for non-Python stacks. Root `tests/` is preserved for stacks that own root tests, currently Python and Web single projects, and removed for Go/Rust single projects whose tests live beside their source files.

**Note:** `SPEC.md` is *not* removed — the scaffold's design spec is replaced by a project-specific correctness envelope generated from `templates/SPEC.md.tmpl`.

## Shared templates

Generated for all stacks and shapes from `templates/`:

```
SPEC.md.tmpl                              →  SPEC.md (correctness envelope)
AGENTS.md.tmpl                            →  AGENTS.md (+ CLAUDE.md symlink)
README.md.tmpl                            →  README.md
docs/README.md.tmpl                              →  docs/README.md
docs/AGENTS.md.tmpl                              →  docs/AGENTS.md
docs/explanation/architecture.md.tmpl            →  docs/explanation/architecture.md
docs/explanation/decision-ledger.md.tmpl         →  docs/explanation/decision-ledger.md
docs/explanation/decisions/0001-stack-choice.md.tmpl  →  docs/explanation/decisions/0001-stack-choice.md
.github/workflows/ci.yml.tmpl            →  .github/workflows/ci.yml
```

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

### Rust

Copies from `stacks/rust/`:

```
Cargo.toml.tmpl  →  Cargo.toml
src/main.rs.tmpl →  src/main.rs
src/lib.rs       →  src/lib.rs
Dockerfile.tmpl  →  Dockerfile
rustfmt.toml     →  rustfmt.toml
README.md        →  README.md
```

### Web

Copies from `stacks/web/project/`:

```
package.json.tmpl                       →  package.json
wrangler.jsonc.tmpl                     →  wrangler.jsonc
index.html.tmpl                         →  index.html
src/                                    →  React browser app
worker/                                 →  Cloudflare Worker API routes
migrations/0001_auth_and_saved_runs.sql →  D1 schema seed
tests/                                  →  Vitest tests
```

Optional web flags alter the copied template after render:

- `--web-ui tailwind` adds Tailwind v4 and the Vite Tailwind plugin.
- `--web-ui shadcn` adds Tailwind plus `components.json`, `src/lib/utils.ts`,
  and `src/components/ui/button.tsx`.
- `--web-db drizzle-d1` keeps the Cloudflare D1 migration/binding and adds
  `worker/db/schema.ts` plus Drizzle query code.

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
