---
id: python-stack
title: Python Stack
description: >
  Python stack tooling: uv for package management, ruff for formatting and linting,
  ty for type checking, and pytest with xdist and coverage for testing.
index:
  - id: tools
    keywords: [uv, ruff, ty, pytest, tools, pyproject]
  - id: formatter-ruff-format
    keywords: [ruff-format, line-length, format, autofix]
  - id: linter-ruff-check
    keywords: [ruff-check, rules, e-w-f-i-b-up-s, lint]
  - id: type-checker-ty
    keywords: [ty, type-check, python-version, error-on-warning]
  - id: test-runner-pytest
    keywords: [pytest, xdist, coverage, parallel, junit, cov]
---

# Python Stack

## Tools

| Purpose | Tool | Config |
|---------|------|--------|
| Package/env management | [uv](https://docs.astral.sh/uv/) | `pyproject.toml` |
| Formatter | [ruff format](https://docs.astral.sh/ruff/) | `[tool.ruff]` |
| Linter | [ruff check](https://docs.astral.sh/ruff/) | `[tool.ruff.lint]` |
| Type checker | [ty](https://docs.astral.sh/ty/) | `[tool.ty]` |
| Test runner | [pytest](https://docs.pytest.org/) | `[tool.pytest.ini_options]` |

All tools are installed automatically via `uv sync --all-extras` during `mise run setup`.

## mise.toml (generated)

```toml
[tools]
python = "3.12"
uv = "latest"
```

## Project layout

```
my-project/
├── pyproject.toml
├── my_project/
│   ├── __init__.py
│   └── example.py
└── tests/
    ├── __init__.py
    └── test_example.py
```

## Formatter — ruff format

Line length 88, enforced on all `.py` files.

```bash
mise run fmt           # format in-place
mise run fmt --check   # check only (used by check/CI)
```

Config in `pyproject.toml`:
```toml
[tool.ruff]
target-version = "py312"
line-length = 88
```

## Linter — ruff check

Runs an extensive rule set covering style, correctness, security, and modern Python idioms.

```bash
mise run lint
```

Enabled rule sets: `E`, `W`, `F`, `I`, `B`, `C4`, `UP`, `N`, `S`, `PTH`, `RUF`.

## Type checker — ty

[ty](https://docs.astral.sh/ty/) is Astral's fast type checker for Python ≥ 3.12.

```bash
mise run typecheck
```

Config in `pyproject.toml`:
```toml
[tool.ty.environment]
python-version = "3.12"
```

!!! note
    ty is under active development. harness-scaffold pins `>=0.0.19`. Check [releases](https://github.com/astral-sh/ty/releases) for updates.

## Test runner — pytest

```bash
mise run test
```

Generated projects include pytest-xdist for parallel test execution and pytest-cov for coverage:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-n auto --dist=loadfile --cov=my_project --cov-report=term-missing -q"
```

## Coverage

pytest-cov is included in generated projects. Reports print to the terminal during `mise run test`.

## Pre-commit parity

The same ruff + ty + pytest commands run in pre-commit hooks via `mise run fmt`, `mise run lint`, `mise run typecheck`, `mise run test` — identical to CI.
