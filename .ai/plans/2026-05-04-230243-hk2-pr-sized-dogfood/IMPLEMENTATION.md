---
id: plan-implementation
title: Implementation Notes
description: >
  Notes about what was executed and why.
---

# IMPLEMENTATION — hk2-pr-sized-dogfood

## Trial setup

Created `/tmp/hk2-pr-sized-trials` with:

- a wrapper CLI at `/tmp/hk2-pr-sized-trials/bin/hk` that runs the current HK
  checkout through `uv --directory` and logs each invocation to
  `/tmp/hk2-pr-sized-trials/hk-commands.jsonl`;
- shallow no-remote snapshots at parent commits for each target repo;
- a reports directory for worker reports and generated handoffs.

The wrapper was necessary because the installed `~/.local/bin/hk` still exposes
an older HK command surface.

## Workers

Launched three parallel `worker` subagents with fresh context:

- <REDACTED_ORG> Ads ML: table_endorsement_scorer coalesce phase.
- <REDACTED_ORG> Ads API: AdSetBuilder DeliveryConfig / delivery_config_json migration.
- Foreman: macOS notification sound and click/lifecycle handling.

Prompting intentionally avoided HK lifecycle walkthroughs. Workers were told to
use HK, begin by exploring the CLI, and write a report with HK commands tried.

## Output

Synthesis artifact:

- `artifacts/pr-sized-dogfood-study.md`

External temp artifacts:

- `/tmp/hk2-pr-sized-trials/hk-commands.jsonl`
- `/tmp/hk2-pr-sized-trials/reports/*-worker-report.md`
- `/tmp/hk2-pr-sized-trials/reports/*-handoff.md`
