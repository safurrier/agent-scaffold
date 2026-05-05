---
id: plan-validation
title: Validation Log
description: >
  How changes were verified. Append entries after testing.
  Link to artifacts — don't store them here. See _example/ for a reference.
---

# Validation

## Commands

- `parallel worker subagent dogfood run` — 3/3 worker tasks succeeded and produced reports under `/tmp/hk2-pr-sized-trials/reports/`.
- Foreman worker: `cargo test notifications --lib --tests` — passed.
- Foreman worker: `mise run check` — passed after fixing a clippy finding.
- `python3 parse /tmp/hk2-pr-sized-trials/hk-commands.jsonl` — parsed wrapper log: Ads ML 30 HK commands / 5 failed, Ads API 32 / 3 failed, Foreman 27 / 5 failed.
- `/tmp/hk2-pr-sized-trials/bin/hk ready --target /tmp/hk2-pr-sized-trials/discord-ads-ml --json` — `ready=false`, `status=not-ready`.
- `/tmp/hk2-pr-sized-trials/bin/hk ready --target /tmp/hk2-pr-sized-trials/discord-ads-api --json` — `ready=false`, `status=not-ready`.
- `/tmp/hk2-pr-sized-trials/bin/hk ready --target /tmp/hk2-pr-sized-trials/foreman --json` — `ready=false`, `status=not-ready`.
- `/tmp/hk2-pr-sized-trials/bin/hk handoff --target <trial> --write /tmp/hk2-pr-sized-trials/reports/<trial>-handoff.md` — generated handoffs for all three trials.

## Evidence

Artifacts listed in `artifacts/manifest.yaml`:

- `artifacts/pr-sized-dogfood-study.md`

External temp artifacts retained for this session:

- `/tmp/hk2-pr-sized-trials/hk-commands.jsonl`
- `/tmp/hk2-pr-sized-trials/reports/discord-ads-ml-worker-report.md`
- `/tmp/hk2-pr-sized-trials/reports/discord-ads-api-worker-report.md`
- `/tmp/hk2-pr-sized-trials/reports/foreman-worker-report.md`
- `/tmp/hk2-pr-sized-trials/reports/discord-ads-ml-handoff.md`
- `/tmp/hk2-pr-sized-trials/reports/discord-ads-api-handoff.md`
- `/tmp/hk2-pr-sized-trials/reports/foreman-handoff.md`

## Notes

This slice validates the dogfood study and artifact capture, not merge-readiness
of the worker implementation diffs.
