---
id: plan-workflow-validation
title: Plan Workflow — Validation
description: >
  How the plan workflow changes were verified.
---

# Validation

## 2026-03-08 — Full test suite

```
mise run check — 363 passed (up from 322)
```

New tests added:
- Contract: plan task exists + executable + shebang + description header
- Contract: plan templates exist (AGENTS.md, _templates/, _example/)
- Contract: example META.yaml is valid
- Contract: plan template required files exist
- Docs contract: example META.yaml validates with correct status
- Golden output: plan templates generated in all 4 shapes (PySingle, PyApps, GoSingle, GoApps)

## 2026-03-08 — E2E: plan task in generated project

Ran full pipeline in tmp dir:

```bash
# Init a project
mise run init -- --non-interactive --name testproject --shape single --stack python --no-hooks
# Verify plan templates shipped
ls .ai/plans/  # → AGENTS.md, _templates/, _example/
# Create a plan on a feature branch
git checkout -b feat/test-plan
mise run plan -- test-feature
# → Created .ai/plans/2026-03-08-0917-test-feature/ with all templates
```

## 2026-03-08 — Pre-push skills run

Ran all 4 pre-push skills (spec-sync, context-engineering, docs-workflow, plan-sync).
Found and fixed: stale task counts, missing docs sections, missing ADR, stale plan artifacts.

## 2026-03-08 — Review follow-up fixes

Targeted regression run:

```bash
uv run pytest tests/e2e/test_plan.py -q -n 0
# 8 passed
```

New coverage added:
- `tests/e2e/test_plan.py` — scaffold repo happy path, invalid slug, duplicate slug,
  generated repo default-branch failure, generated repo feature-branch success
- `tests/unit/test_golden_output.py` — generated README and AGENTS include the plan workflow

Full validation after fixes:

```bash
mise run check
# 363 passed
```
