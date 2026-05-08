---
id: plan-validation
title: Validation Evidence
description: >
  Commands run and what they proved.
---

# VALIDATION — hk-summary-skip-mitigation

## Commands

```bash
uv run pytest tests/unit/test_harness_kit_2.py::test_dangerously_skip_sync_satisfies_readiness_and_handoff tests/unit/test_harness_kit_2.py::test_dangerously_skip_sync_requires_prior_checkpoint tests/unit/test_harness_kit_2.py::test_dangerously_skip_sync_goes_stale_after_later_work tests/unit/test_harness_kit_2.py::test_cli_handoff_pr_format_discloses_dangerous_skips tests/unit/test_harness_kit_2.py::test_cli_dangerously_skip_requires_mitigation tests/unit/test_harness_kit_2.py::test_cli_summary_renders_human_readiness_digest -q
```

Result: passed, 6 tests.

```bash
uv run ruff check src/harness_toolkit/kit/cli.py src/harness_toolkit/kit/app/lifecycle.py src/harness_toolkit/kit/local.py src/harness_toolkit/kit/readiness/policy.py src/harness_toolkit/kit/rendering/handoff.py src/harness_toolkit/kit/ledger/store.py tests/unit/test_harness_kit_2.py tests/unit/test_hk2_lifecycle_parity.py tests/unit/test_portable_workflow.py
```

Result: passed.

```bash
uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_hk2_lifecycle_parity.py tests/unit/test_portable_workflow.py -q
```

Result: passed, 97 tests.

```bash
# Synthetic rollout dogfood in /tmp/hk-summary-skip-dogfood/repo.
scripts/hk-dev start summary-skip --target . --json
scripts/hk-dev start summary-skip --target . --json
scripts/hk-dev plan 'Implement tiny README update' --target . --json
scripts/hk-dev plan 'Record validation and risky review skip' --target . --json
scripts/hk-dev validate --why 'Smoke command proves HK command capture works' --target . -- python3 -c 'print("ok")'
scripts/hk-dev dangerously-skip review --label no-review --reason 'Synthetic dogfood has no separate reviewer' --mitigation 'Focused unit tests and local CLI dogfood cover this change' --target . --json
scripts/hk-dev decide 'Synthetic dogfood only; no product behavior change' --spec-impact not-needed --target . --json
scripts/hk-dev sync --target . --json
scripts/hk-dev ready --target . --json
scripts/hk-dev summary --target .
```

Result: passed. The same-slug retry returned `resumed: true`; final readiness was `ready-with-dangerous-skips`; summary rendered validation transcript, review skip label, reason, and mitigation.

Evidence: `artifacts/summary-skip-dogfood.log`.

```bash
mise run check
```

Result: passed. Full gate completed with 836 tests passing.

```bash
uv run mkdocs build --strict --site-dir /tmp/harness-toolkit-summary-skip-docs
```

Result: passed. MkDocs emitted its existing Material/MkDocs compatibility warning and existing `docs/AGENTS.md` nav notice; strict build completed successfully.

After review fixes, reran:

```bash
mise run check
uv run mkdocs build --strict --site-dir /tmp/harness-toolkit-summary-skip-docs
```

Result: passed again. Full gate completed with 836 tests passing; strict docs build completed successfully with the same existing warnings/notices.
