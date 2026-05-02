---
id: plan-implementation
title: Implementation Notes
description: >
  Notes about the implementation path for release/install documentation.
---

# Implementation — release-install-pattern

## Summary

Added GitHub/uv-tool based install and release documentation without adding PyPI
publishing. The docs now distinguish portable CLI installation from clone-and-init
scaffold usage.

## Changes

- Added `docs/release.md` with:
  - latest GitHub install
  - pinned tag install
  - editable local checkout install
  - upgrade/reinstall commands
  - GitHub tag release checklist
  - PyPI deferral notes
- Updated `README.md`, `docs/getting-started.md`, `docs/index.md`, and
  `docs/portable-workflow.md` to surface the install path.
- Added `release.md` to `mkdocs.yml` and `docs/AGENTS.md`.
- Added `readme`, author, and project URLs to `pyproject.toml`.

## Validation Notes

Docs/frontmatter/reference checks passed. `uv build` produced sdist and wheel
successfully; local `dist/` artifacts were removed. `mise run check` passed with
723 tests.
