---
id: plan-spec
title: Scope Specification
description: >
  Slice-local scope and acceptance criteria.
---

# SPEC — hk2-pr-sized-dogfood

## Goal

Run a more realistic HK 2.0 dogfood study using parallel worker subagents on
PR-sized tasks in:

- <REDACTED_ORG> monorepo Ads ML area;
- <REDACTED_ORG> monorepo Ads API area;
- Foreman.

Workers should receive little HK-specific guidance beyond using HK and exploring
its CLI to onboard. The study should measure how agents actually move through HK,
where they skip it, and where they misuse or misunderstand it.

## Scope

- Prepare temporary/shallow repo snapshots so original repos are untouched.
- Run three parallel worker subagents on PR-sized implementation directives.
- Capture worker reports and HK command logs.
- Generate parent-observed handoffs/readiness after the run.
- Produce a synthesis report with complete HK usage path and product findings.

## Out of scope

- Merging or preserving worker implementation diffs.
- Completing external review of worker implementation quality.
- Fixing HK product issues found by this study in the same slice.

## Acceptance

- All three workers run and produce reports.
- The study artifact records where HK was used, not used, and used incorrectly.
- The artifact records final readiness state for each trial.
- Original repos remain untouched.
