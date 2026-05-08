---
id: plan-validation
title: Validation Evidence
description: >
  Commands run and what they proved.
---

# VALIDATION — hk-agent-adoption-dogfood

## Commands

```bash
ROOT=/tmp/hk-agent-adoption-trial
# create temp repo, hk logging wrapper, and AGENTS.md from scripts/hk-dev instructions --scope user
```

Result: passed. Temp repo created with only the generated Harness Kit snippet in
`AGENTS.md`.

```bash
PATH="$ROOT/bin:$PATH" HK_DOGFOOD_LOG="$ROOT/hk-commands.jsonl" codex exec --skip-git-repo-check "Add a small Python utility function and tests for it. Do not commit. When done, write /tmp/hk-agent-adoption-trial/worker-report.md summarizing what you changed and what validation you ran."
```

Result: passed. Codex completed the implementation and wrote the report without
committing.

```bash
cat /tmp/hk-agent-adoption-trial/hk-commands.jsonl
git -C /tmp/hk-agent-adoption-trial/repo status --short
find /tmp/hk-agent-adoption-trial/repo/.harness-local -maxdepth 5 -type f
```

Result: confirmed HK was used from the AGENTS.md snippet. Final status showed only
source changes and untracked source/test dirs; HK local state remained under
`.harness-local`.

```bash
python3 /Users/alex.furrier/.pi/agent/skills/alex-ai-skill-creator/scripts/quick_validate.py .agent/skills/hk-pr-sized-dogfood
```

Result: passed. Also cleaned older angle-bracket placeholders in the skill so the validator accepts it.

```bash
uv run pytest tests/unit/test_portable_workflow.py -q
```

Result: passed, 15 tests. This is a focused regression check for the `hk instructions` behavior used by the dogfood variant.

## Evidence

- `artifacts/adoption-trial-summary.md`
- `artifacts/adoption-trial-hk-commands.jsonl`
- `artifacts/adoption-trial-worker-report.md`
- `artifacts/agents-md-relevance-review.md`
