---
id: repo-shapes
title: Repo Shapes
description: >
  The two repo shapes — single-project and apps workspace — their layouts,
  workspace.toml structure, and how tasks behave differently per shape.
index:
  - id: single-project
    keywords: [single, layout, root, one-language]
  - id: apps-workspace
    keywords: [apps, packages, workspace-toml, modules, monorepo, multi-module]
  - id: choosing-a-shape
    keywords: [choose, comparison, criteria, when-to-use]
---

# Repo Shapes

harness-scaffold supports two repo shapes selected at `init` time.

## Single-project

One language, one root package. The default.

```
my-project/
├── .mise.toml
├── .github/workflows/ci.yml
├── pyproject.toml          # Python: package config + tool config
├── go.mod                  # Go: module config
│
├── src/my_project/         # Python: source package
│   ├── __init__.py
│   └── example.py
├── cmd/main.go             # Go: entry point
├── internal/app/           # Go: core logic
│   ├── app.go
│   └── app_test.go
│
└── tests/                  # Python: test suite
    └── test_example.py
```

All `mise run` tasks operate at the repo root.

## Apps workspace

Multiple apps and/or packages under a single repo. Declared via `workspace.toml`.

```
my-platform/
├── .mise.toml
├── workspace.toml          # module registry
│
├── apps/
│   ├── api/                # Python service
│   │   ├── pyproject.toml
│   │   └── api/
│   └── worker/             # Python worker
│       ├── pyproject.toml
│       └── worker/
│
└── packages/               # shared libraries (optional)
    └── common/
```

### workspace.toml

The module registry lists every app/package that mise tasks should iterate over:

```toml
[modules.api]
path = "apps/api"
kind = "python"
role = "app"

[modules.worker]
path = "apps/worker"
kind = "python"
role = "app"
```

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `path` | No | string | Path relative to repo root (default: `apps/<name>`) |
| `kind` | No | `python`, `go`, `rust` | Stack for this module |
| `role` | No | `app`, `package` | Module role |

### Task behaviour in apps shape

When `SCAFFOLD_PROJECT_SHAPE=apps`, every task iterates `workspace.toml` and runs per-module:

```
==> [api] fmt
  ✓ [api] fmt
==> [worker] fmt
  ✓ [worker] fmt
```

Failures are collected across all modules — all modules run even if one fails — then the task exits non-zero if any module failed.

## Choosing a shape

| | Single | Apps |
|--|--------|------|
| Languages | One | Multiple (mixed) |
| Shared packages | No | Yes, under packages/ |
| `workspace.toml` | Not used | Required |
| Task scope | Repo root | Per-module |
| When to use | Most projects | Monorepos, platforms |
