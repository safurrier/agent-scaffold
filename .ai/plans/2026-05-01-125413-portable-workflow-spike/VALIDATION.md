---
id: plan-validation
title: Validation Log
description: >
  How changes were verified. Append entries after testing.
  Link to artifacts — don't store them here. See _example/ for a reference.
---

# Validation

## Commands

- `uv run pytest tests/unit/test_portable_workflow.py -q` — passed after iterating on git hook isolation and local review placeholder handling.
- `uv run ruff format src/harness_toolkit/cli.py src/harness_toolkit/kit/workflow.py tests/unit/test_portable_workflow.py` — formatted changed Python files.
- `uv run ruff check src/harness_toolkit/cli.py src/harness_toolkit/kit/workflow.py tests/unit/test_portable_workflow.py` — passed.
- `uv run ty check src/harness_toolkit tests/unit/test_portable_workflow.py` — passed.
- `uv run pytest tests/unit/test_portable_workflow.py tests/unit/test_cli.py -q` — passed before Cyclopts migration.
- `uv run agent-workflow instructions --json` — passed and returned the minimal `AGENTS.md` snippet as JSON.
- `uv run agent-workflow plan --help` — passed and showed copyable examples in help output.
- `uv run pytest tests/unit/test_portable_workflow.py tests/unit/test_cli.py -q` — passed after Cyclopts migration, 17 tests.
- `uv run agent-workflow profiles --json` — passed and listed built-in profile DSL packages.
- `uv run agent-workflow checks --profile python --target /Users/alex.furrier/git_repositories/agent-scaffold --json` — passed and returned named check templates without executing validation commands.
- `uv run pytest tests/unit/test_portable_workflow.py -q` — passed after profile DSL implementation, 9 tests.
- Private/company-specific term scan across public repo docs, source, tests, and this plan — no matches after public-profile cleanup.
- `uv run ruff format src/harness_toolkit/agent_workflow_cli.py src/harness_toolkit/kit/profiles.py tests/unit/test_portable_workflow.py` — formatted public-profile cleanup.
- `uv run ruff check src/harness_toolkit/agent_workflow_cli.py src/harness_toolkit/kit/profiles.py src/harness_toolkit/kit/workflow.py tests/unit/test_portable_workflow.py` — passed after public-profile cleanup.
- `uv run ty check src/harness_toolkit tests/unit/test_portable_workflow.py` — passed after public-profile cleanup.
- `uv run pytest tests/unit/test_portable_workflow.py tests/unit/test_cli.py -q` — passed after public-profile cleanup, 18 tests.
- `uv run pytest -m "contract or unit" -q` — passed after public-profile cleanup, 427 tests.
- `mise run sync-check` — passed after public-profile cleanup.
- `uv run pytest tests/unit/test_cli.py -q` — passed after Cyclopts migration for `agent-scaffold init`, 9 tests.
- `uv run pytest tests/unit/test_portable_workflow.py -q` — passed after removing `--module` scope, 10 tests.
- `uv run ruff check src/harness_toolkit/cli.py src/harness_toolkit/scaffold/prompts.py src/harness_toolkit/scaffold/init.py src/harness_toolkit/agent_workflow_cli.py src/harness_toolkit/kit/workflow.py tests/unit/test_cli.py tests/unit/test_portable_workflow.py` — passed after Click removal and scope refactor.
- `uv run ty check src/harness_toolkit tests/unit/test_cli.py tests/unit/test_portable_workflow.py` — passed after Click removal and scope refactor.
- `uv run agent-scaffold init --non-interactive --name cycloptsdemo --shape single --stack python --no-hooks --no-examples` in a copied temp scaffold — passed.
- `rg -n "click|Click|CliRunner" src tests pyproject.toml` — no matches after Cyclopts migration.
- `uv run pytest -m "contract or unit" -q` — passed after updating entrypoint contract for Cyclopts `main`, 427 tests.
- `mise run sync-check` — passed after Click removal and scope refactor.
- `mise run check` — passed after Click removal and scope refactor, including 693 pytest items.
- `rg -n -- "--module|module key|Optional module|module=module|module: str" src/harness_toolkit/agent_workflow_cli.py src/harness_toolkit/kit/workflow.py docs/portable-workflow.md tests/unit/test_portable_workflow.py` — no matches after removing `--module` workflow scope.
- `rg -n "click|Click|CliRunner" src tests pyproject.toml` — no matches after full Cyclopts migration.
- `mise run check` — passed after final no-Click/no-module scans, including 693 pytest items.
- `uv run pytest -m "contract or unit" -q` — passed after full `harness_toolkit` package rename, including 431 tests.
- `mise run check` — passed after clean `harness-toolkit` / `harness-scaffold` / `hk` rename, including 703 pytest items.
- `mise run sync-check -- --plan-dir .ai/plans/2026-05-02-083917-harness-kit-naming` — passed after completing the naming plan contract.
- `mise run sync-check` — passed for the active portable workflow plan after reflected paths were updated to `src/harness_toolkit/kit/cli.py`.
- Foreman temp-copy parallel dogfood: cloned foreman twice under `/tmp/agent-workflow-foreman-e2e-20260501150510`, dispatched one agent using portable `agent-workflow` and one using native repo workflow. Portable run created external plan state, ran `git diff --check`, `mise trust .mise.toml && mise run check`, and portable `agent-workflow sync-check` successfully. Native run created repo-local plan state and ran `mise run check`/`git diff --check`, but `mise run sync-check` failed because that foreman checkout has no `sync-check` task despite repo guidance mentioning it.
- Foreman profile-selection dogfood: cloned foreman under `/tmp/agent-workflow-foreman-profile-e2e-20260501151808`, dispatched an agent with instructions to run `agent-workflow profiles --target ... --json` first and use the closest profile. The agent selected `rust-mise`, used `mise run check` as the fast gate, recovered from temp-copy mise trust with `mise trust .mise.toml && mise run check`, and passed portable `agent-workflow sync-check`. It also exposed an ergonomics gap by passing `--state-root` to `checks`; `checks` and `profiles` now accept `--mode`/`--state-root` for command-shape consistency without reading or writing state.
- Custom profile side-by-side dogfood: cloned foreman twice under `/tmp/agent-workflow-custom-profile-e2e-20260502084815`. Built-ins-only run selected `rust-mise` as the closest built-in profile, ran `mise trust .mise.toml && mise run check`, and passed portable sync-check. Custom-profile run loaded `/tmp/agent-workflow-custom-profile-e2e-20260502084815/profiles/foreman-root.toml`, selected `foreman-root` over built-in `rust-mise` because it exactly matched the Foreman repo target, ran the same fast gate, and passed portable sync-check. Both runs left only `docs/getting-started.md` untracked in the target repo, aside from `.pi/` harness scratch in the custom run.
- `uv run pytest -m "contract or unit" -q` — passed, 427 tests.
- `mise run sync-check` — passed for this active plan.
- `mise run check` — passed before Cyclopts migration, including 688 pytest items.
- `uv run pytest -m "contract or unit" -q` — passed after Cyclopts migration, 427 tests.
- `mise run sync-check` — passed after Cyclopts migration for this active plan.
- `mise run check` — passed after Cyclopts migration, including 691 pytest items.
- Manual smoke: cloned `/Users/alex.furrier/git_repositories/dread` into `/tmp/agent-scaffold-portable-spike/dread`, ran external `workflow plan/status/sync-check`, and confirmed `git status --porcelain` was empty.
- Manual smoke after Cyclopts migration: cloned `dread` into `/tmp/agent-scaffold-portable-spike-cyclopts/dread`, ran external `agent-workflow plan/status/sync-check`, and confirmed `git status --porcelain` was empty.
- Manual smoke: ran overlay `workflow attach` against the cloned `dread` repo and confirmed `.git/info/exclude` ignored `/.ai-local/agent-scaffold/` while `git status --porcelain` stayed empty.

## Evidence

- Command output recorded in the agent session; no durable artifact required for this spike beyond this validation log.
