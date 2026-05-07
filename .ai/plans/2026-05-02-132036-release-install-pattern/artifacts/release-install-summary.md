# Release Install Summary

The release/install docs now describe GitHub-sourced uv tool installs instead of
PyPI install-by-name:

```bash
uv tool install git+https://github.com/safurrier/harness-toolkit.git
uv tool install git+https://github.com/safurrier/harness-toolkit.git@v0.1.0
uv tool install --editable ~/git_repositories/harness-toolkit
```

The documented release boundary is a GitHub tag plus GitHub release. PyPI is
explicitly deferred until the CLI/profile contracts settle.
