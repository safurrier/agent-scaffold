---
id: release
title: Release and Installation
description: >
  How to install Harness Toolkit CLIs with uv tool and cut GitHub tag releases
  before PyPI publishing is needed.
index:
  - id: install-cli-tools
    keywords: [uv, tool, install, hk, harness-kit, harness-scaffold]
  - id: release-policy
    keywords: [versioning, tags, github-release, pypi]
  - id: release-checklist
    keywords: [check, build, tag, release]
---

# Release and Installation

Harness Toolkit is currently distributed as a GitHub-sourced Python tool. PyPI
publishing is intentionally deferred until the command contract settles.

## Install CLI tools

Install the latest `main` from GitHub:

```bash
uv tool install git+https://github.com/safurrier/harness-toolkit.git
```

Install a pinned release tag:

```bash
uv tool install git+https://github.com/safurrier/harness-toolkit.git@v0.1.0
```

Install from a local checkout for development:

```bash
git clone https://github.com/safurrier/harness-toolkit.git
uv tool install --editable ./harness-toolkit
```

Verify the installed commands:

```bash
hk --version
harness-kit --version
harness-scaffold --version
```

The installed executables are:

| Command | Use |
|---|---|
| `hk` | Daily portable workflow command for existing repos |
| `harness-kit` | Readable alias for `hk` |
| `harness-scaffold` | Starter-template CLI for initializing new repos |

## Upgrade or reinstall

Upgrade a GitHub-sourced install:

```bash
uv tool upgrade harness-toolkit
```

Reinstall from a specific tag when you want to force the source:

```bash
uv tool install --reinstall git+https://github.com/safurrier/harness-toolkit.git@v0.1.0
```

For editable local installs, pull the checkout and reinstall when entry points or
dependencies change:

```bash
git -C ~/git_repositories/harness-toolkit pull --ff-only
uv tool install --editable ~/git_repositories/harness-toolkit --force
```

## Release policy

Use GitHub tags/releases as the distribution boundary for now.

- Keep `0.x` while CLI contracts and profile semantics are still settling.
- Use patch releases for bug fixes, documentation, and validation hardening.
- Use minor releases for command, profile, or plan-contract changes.
- Defer PyPI until external install-by-name is worth the package maintenance.

## Release checklist

Before tagging:

```bash
mise run check
mise run sync-check
uv build
```

Then create and publish the tag:

```bash
git tag v0.1.0
git push origin v0.1.0
gh release create v0.1.0 --title "v0.1.0" --notes "$(cat <<'NOTES'
## Summary
- Initial Harness Toolkit release.

## Install
uv tool install git+https://github.com/safurrier/harness-toolkit.git@v0.1.0
NOTES
)"
```

After publishing, verify from a clean environment when possible:

```bash
uv tool install --reinstall git+https://github.com/safurrier/harness-toolkit.git@v0.1.0
hk --version
harness-scaffold --version
```

## PyPI later

Before publishing to PyPI, add or verify:

- project metadata in `pyproject.toml`
- license metadata
- package URLs and classifiers
- GitHub Actions release workflow using trusted publishing
- TestPyPI dry run

Until then, prefer explicit GitHub tag installs so users know exactly what source
they installed.
