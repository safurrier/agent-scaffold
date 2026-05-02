---
id: getting-started
title: Getting Started
description: >
  Step-by-step guide to installing mise, cloning harness-toolkit, and running
  mise run init to initialize a new project interactively or non-interactively.
index:
  - id: prerequisites
    keywords: [mise, install, homebrew, curl, winget, path]
  - id: initialize-a-project
    keywords: [init, interactive, non-interactive, name, shape, stack]
  - id: after-init
    keywords: [setup, check, dev, next-steps]
---

# Getting Started

## Prerequisites

Only **mise** needs to be on your `PATH`. It manages everything else.

=== "macOS / Linux (curl)"
    ```bash
    curl https://mise.run | sh
    ```

=== "macOS (Homebrew)"
    ```bash
    brew install mise
    ```

=== "Windows (PowerShell)"
    ```powershell
    winget install jdx.mise
    ```

Once mise is installed, `mise install` pulls down all tools declared in `.mise.toml` — currently Python and uv for the scaffold itself, then stack-specific tooling after `init`.

## Initialize a project

### Interactive

```bash
git clone https://github.com/safurrier/harness-toolkit.git my-project
cd my-project
mise install
mise run init
```

The interactive flow prompts for:

1. **Project name** — lowercase, hyphens allowed (e.g. `my-service`)
2. **Description** — one-line project description
3. **Shape** — `single` (one language) or `apps` (workspace with multiple apps)
4. **Stack** — `python` or `go`
5. **Author** name and email
6. **Options** — pre-commit hooks, example code

### Non-interactive

```bash
mise run init -- \
  --non-interactive \
  --name my-service \
  --shape single \
  --stack python
```

Full flag reference:

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--name` | Yes | — | Project name (lowercase, hyphens) |
| `--description` | No | `A <name> project` | One-line description |
| `--shape` | No | `single` | `single` or `apps` |
| `--stack` | No | `python` | `python` or `go` |
| `--modules` | For apps | — | Comma-separated module names |
| `--go-module` | For Go | `github.com/your-org/<name>` | Go module path |
| `--author-name` | No | — | Author name |
| `--author-email` | No | — | Author email |
| `--no-hooks` | No | hooks enabled | Skip pre-commit installation |
| `--no-examples` | No | examples kept | Remove example source files |

## After init

```bash
mise run setup   # install dependencies
mise run check   # verify everything passes
mise run dev     # start developing
```

!!! tip "What init does"
    See [Init System](init-system.md) for a detailed walkthrough of everything `mise run init` does to transform the scaffold into your project.
