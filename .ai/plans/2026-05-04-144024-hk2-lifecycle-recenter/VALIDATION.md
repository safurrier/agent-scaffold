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
uv run pytest tests/unit/test_harness_kit_2.py tests/e2e/test_harness_kit_rollout.py -q
```

Result:

```text
24 passed in 34.13s
```

```bash
mise run check
```

Result:

```text
759 passed in 167.98s
All checks passed
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
