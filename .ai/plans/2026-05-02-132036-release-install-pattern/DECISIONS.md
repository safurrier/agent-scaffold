# Decisions

## What Changed

- Added `docs/release.md` with uv tool install commands, GitHub tag release checklist, upgrade/reinstall commands, and PyPI deferral guidance.
- Updated README, getting-started, docs index, portable workflow docs, mkdocs nav, and docs AGENTS index to surface the install/release path.
- Added minimal `pyproject.toml` package metadata (`readme`, author, project URLs) so built distributions carry useful links.

## Why

- Harness Toolkit needs a clear install path for `hk`, `harness-kit`, and `harness-scaffold` before PyPI publishing is worth the maintenance overhead.
- GitHub tag installs via `uv tool install git+...@vX.Y.Z` are enough for a personal 0.x release workflow.
- PyPI can wait until the CLI/profile contract settles and broader install-by-name distribution is useful.
