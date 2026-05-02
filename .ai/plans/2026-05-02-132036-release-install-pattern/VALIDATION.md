# Validation

## Commands

- `hk instructions --profile generic --json`
  - Result: printed the portable workflow instructions used to start this slice.
- `hk profile list --target . --json`
  - Result: listed built-in profiles. Chose `generic` because this repo has a repo-native mise contract and no exact Harness Toolkit profile yet.
- `hk plan release-install-pattern --target . --profile generic --json`
  - Result: created this external Harness Kit plan.
- `hk checks --target . --profile generic --json`
  - Result: directed validation to the repo-native fast gate plus `hk sync-check`.
- `python3 /Users/alex.furrier/.pi/agent/skills/alex-ai-docs-workflow/scripts/docs_verify.py /Users/alex.furrier/git_repositories/agent-scaffold`
  - Result: passed.
- `python3 /Users/alex.furrier/.pi/agent/skills/alex-ai-ai-context-engineering-files/scripts/validate_frontmatter.py /Users/alex.furrier/git_repositories/agent-scaffold`
  - Result: initially failed because `docs/release.md` frontmatter id did not match the generated heading; passed after changing `install-cli` to `install-cli-tools`.
- `python3 /Users/alex.furrier/.pi/agent/skills/alex-ai-ai-context-engineering-files/scripts/verify_references.py /Users/alex.furrier/git_repositories/agent-scaffold`
  - Result: passed.
- `uv build`
  - Result: built sdist and wheel successfully; removed local `dist/` afterward.

## Evidence

- `docs/release.md` contains the release/install pattern.
- `README.md`, `docs/getting-started.md`, `docs/index.md`, and `docs/portable-workflow.md` link or inline the uv tool install path.
- `git status --porcelain`
  - Result: used before handoff to confirm only intended docs/package metadata changes remain.
- `mise run check`
  - Result: passed after release/install documentation and package metadata updates; 723 tests.
