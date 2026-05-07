---
id: plan-validation
title: Validation Log
description: >
  How changes were verified. Append entries after testing.
  Link to artifacts — don't store them here. See _example/ for a reference.
---

# Validation

## Commands

- `uv run pytest tests/unit/test_harness_kit_2.py -q` — 31 passed before full gate.
- `uv run pytest tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q` — 23 passed before full gate.
- `uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q` — 54 passed in 43.73s after follow-up review fixes.
- `mise run check` — 768 passed in 152.61s; formatting, lint, typecheck, and full tests passed after follow-up review fixes.
- `subagent reviewer` — no code blockers after follow-up docs fix; reviewer also ran focused tests and full check.
- `mise run sync-check -- --plan-dir .ai/plans/2026-05-05-072708-hk2-dogfood-ux-fixes` — passed plan/spec/evidence/review contract.
- `parallel worker subagent dogfood rerun` — 3/3 worker tasks succeeded and produced reports under `/tmp/hk2-pr-sized-trials-v2/reports/`.
- `/tmp/hk2-pr-sized-trials-v2/bin/hk ready --target /tmp/hk2-pr-sized-trials-v2/<REDACTED_ORG>-ads-ml --json` — `ready=false`, `status=not-ready`; expected missing review plus `.pi` sync warning.
- `/tmp/hk2-pr-sized-trials-v2/bin/hk ready --target /tmp/hk2-pr-sized-trials-v2/<REDACTED_ORG>-ads-api --json` — `ready=false`, `status=not-ready`; expected missing lifecycle records/review plus `.pi` sync warning.
- `/tmp/hk2-pr-sized-trials-v2/bin/hk ready --target /tmp/hk2-pr-sized-trials-v2/foreman --json` — `ready=false`, `status=not-ready`; expected missing decision/review plus `.pi` sync warning.

## Evidence

Artifacts listed in `artifacts/manifest.yaml`:

- `artifacts/pr-sized-dogfood-rerun.md`

External temp artifacts retained for this session:

- `/tmp/hk2-pr-sized-trials-v2/hk-commands.jsonl`
- `/tmp/hk2-pr-sized-trials-v2/reports/<REDACTED_ORG>-ads-ml-worker-report.md`
- `/tmp/hk2-pr-sized-trials-v2/reports/<REDACTED_ORG>-ads-api-worker-report.md`
- `/tmp/hk2-pr-sized-trials-v2/reports/foreman-worker-report.md`
- `/tmp/hk2-pr-sized-trials-v2/reports/<REDACTED_ORG>-ads-ml-handoff.md`
- `/tmp/hk2-pr-sized-trials-v2/reports/<REDACTED_ORG>-ads-api-handoff.md`
- `/tmp/hk2-pr-sized-trials-v2/reports/foreman-handoff.md`

## Notes

The dogfood rerun validates HK workflow behavior, not merge-readiness of worker
implementation diffs.
