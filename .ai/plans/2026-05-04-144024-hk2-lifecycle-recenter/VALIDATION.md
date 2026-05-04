---
id: plan-validation
title: Validation Log
---

# Validation

## Commands

```bash
uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_script_contract_prototype.py -q
```

Result:

```text
21 passed in 25.63s
```

```bash
uv run pytest tests/unit/test_harness_kit_2.py -q
```

Result:

```text
22 passed in 34.70s
```

```bash
uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q
```

Result:

```text
46 passed in 38.62s
```

```bash
mise run check
```

Result:

```text
760 passed in 144.84s
All checks passed
```

Dogfood validation captured through HK 2.0 itself:

```bash
uv run hk validate --target . --kind check --why "Full repo quality gate after lifecycle readiness fixes." --json -- mise run check
```

Result:

```text
760 passed in 168.10s
All checks passed
```

```bash
uv run hk ready --target . --json
```

Result:

```json
{"ready": true, "status": "ready"}
```

```bash
mise run sync-check -- --changed-plans main...HEAD
```

Result:

```text
Sync-check passed
```

```bash
mise run sync-check -- --plan-dir .ai/plans/2026-05-04-144024-hk2-lifecycle-recenter
```

Result:

```text
Sync-check passed
```

## Evidence

- `artifacts/product-postmortem.md` captures the product correction and migration sketch.
- `artifacts/lifecycle-implementation-plan.md` captures the task breakdown, validation plan, dogfood rollout, open questions, and latest decisions on export/dangerous skips/profiles.
- HK-on-HK dogfood work is stored locally under `.harness-local/harness-kit/root/work/2026-05-04-162253-hk2-lifecycle-dogfood/` and includes `hk validate`, `hk review add`, `hk ready`, and `hk export` records.
- `artifacts/subagent-dogfood-findings.md` captures the independent subagent build trial on `/tmp/hk2-subagent-trial`.
