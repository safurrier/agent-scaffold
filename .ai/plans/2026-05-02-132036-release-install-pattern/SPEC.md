---
id: plan-spec
title: Release Install Pattern Specification
description: >
  Requirements and constraints for documenting the Harness Toolkit install and
  release pattern before PyPI publishing.
---

# Specification — release-install-pattern

## Problem

Harness Toolkit now has globally installable CLIs (`hk`, `harness-kit`, and
`harness-scaffold`), but the docs did not clearly explain how to install them as
uv tools or how to cut early GitHub-tag releases. The project is not ready to
promise PyPI install-by-name yet, so release docs need to make the current GitHub
source/tag workflow explicit.

## Requirements

### MUST

- Document `uv tool install` for latest GitHub, pinned tag, and editable local checkout.
- Document verification commands for all installed console scripts.
- Add a release checklist that includes local validation, package build, tag push, and `gh release create`.
- State that PyPI publishing is deferred for now.
- Link the release/install guidance from the main docs surfaces.

### SHOULD

- Add minimal package metadata so built artifacts carry useful project links.
- Keep release docs short enough to follow during a real tag cut.
- Use GitHub tags as the stable install boundary for `0.x` releases.

## Constraints

- Do not add PyPI publishing automation yet.
- Do not claim `uv tool install harness-toolkit` works until the package is published.
- Keep the docs compatible with the current repository URL: `<GITHUB_OWNER>/harness-toolkit`.
