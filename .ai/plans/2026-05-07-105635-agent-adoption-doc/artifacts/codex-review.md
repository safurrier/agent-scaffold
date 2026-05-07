**Findings**

- **Blocking:** `hk instructions --profile python --json` now silently ignores `--profile` because `scope` defaults to `user`, and `profile` is only used when `scope == "repo"`. This is a CLI UX regression for existing callers and also makes `--profiles-dir` a no-op in the same path. Either reject `--profile/--profiles-dir` with `--scope user`, or make an explicit profile imply repo scope. Add a regression test for `hk instructions --profile python --json`.  
  [src/harness_toolkit/kit/cli.py](/Users/alex.furrier/git_repositories/harness-toolkit/src/harness_toolkit/kit/cli.py:161)  
  [src/harness_toolkit/kit/cli.py](/Users/alex.furrier/git_repositories/harness-toolkit/src/harness_toolkit/kit/cli.py:183)  
  [tests/unit/test_portable_workflow.py](/Users/alex.furrier/git_repositories/harness-toolkit/tests/unit/test_portable_workflow.py:98)

No blocking finding on the user-level snippet forcing generic profiles: it uses `hk profile resolve --target . --json` and does not hard-code `--profile generic`.

I did not run the test suite; the local `scripts/hk-dev` check was blocked by the read-only sandbox trying to access the uv cache.
