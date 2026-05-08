No blocking findings.

Confirmed:
- `hk instructions --profile python --json` compatibility is handled. The staged code makes `--profile` imply `scope="repo"` when `--scope` is omitted, then emits `profile: python`.
  [cli.py](/Users/alex.furrier/git_repositories/harness-toolkit/src/harness_toolkit/kit/cli.py:184)
  [test_portable_workflow.py](/Users/alex.furrier/git_repositories/harness-toolkit/tests/unit/test_portable_workflow.py:131)

- The user-level snippet does not force generic profiles. It starts with `hk profile resolve --target . --json` and has no `--profile generic`.
  [cli.py](/Users/alex.furrier/git_repositories/harness-toolkit/src/harness_toolkit/kit/cli.py:82)
  [agent-adoption.md](/Users/alex.furrier/git_repositories/harness-toolkit/docs/agent-adoption.md:31)
  [test_portable_workflow.py](/Users/alex.furrier/git_repositories/harness-toolkit/tests/unit/test_portable_workflow.py:98)

I also executed `.venv/bin/hk instructions --profile python --json` and `.venv/bin/hk instructions --scope user --json`; both matched the intended behavior. `scripts/hk-dev` was blocked by the read-only sandbox’s `uv` cache access, so I used the existing venv entrypoint.
