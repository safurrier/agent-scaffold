---
id: plan-validation
title: Validation Evidence
description: >
  Commands run and what they proved.
---

# VALIDATION — harness-kit-versionless-docs

## Commands

```bash
rg -n "Harness Kit 2|HK2|HK 2|HK1|HK 1|harness-kit-2|hk-2|2\.0" README.md SPEC.md docs mkdocs.yml src/harness_toolkit/kit .agent/skills/hk-pr-sized-dogfood .agent/skills/hk-session-artifacts templates/.agent/skills/harness-kit-profile-authoring -g "*.md" -g "*.py" -g "*.yml" -g "*.yaml"
```

Result: only the generated `context-engineering@2.2.0` comment in `docs/AGENTS.md` matched. Saved in `artifacts/docs-validation.log`.

```bash
uv run mkdocs build --strict --site-dir /tmp/harness-toolkit-docs-review
```

Result: passed. MkDocs emitted its external Material/MkDocs compatibility warning, then built the renamed nav successfully.

```bash
uv run pytest tests/unit/test_harness_kit_2.py tests/e2e/test_harness_kit_rollout.py tests/e2e/test_hk2_cli_parity.py -q
```

Result: `78 passed in 80.31s`.

```bash
codex exec --json -o /tmp/hk-versionless-docs-codex/review.md "Review the current uncommitted docs-only changes ..." > /tmp/hk-versionless-docs-codex/events.jsonl
codex exec --json -o /tmp/hk-versionless-docs-codex-final/review.md "Re-review the current uncommitted changes after fixes ..." > /tmp/hk-versionless-docs-codex-final/events.jsonl
```

Result: final Codex review reported no blocking findings. Codex emitted an MCP token-refresh warning during the run, but produced review output.

## Evidence

- `artifacts/docs-validation.log`
- `artifacts/codex-initial-review.md`
- `artifacts/codex-final-review.md`
