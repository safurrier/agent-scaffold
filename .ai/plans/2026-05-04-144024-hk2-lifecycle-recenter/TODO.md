---
id: plan-todo
title: Task List
description: >
  Checkable tasks for this unit of work. Check off as you go.
---

# TODO — hk2-lifecycle-recenter

- [x] Capture the HK 2.0 product-direction postmortem.
- [x] Record the correction in durable repo context.
- [x] Add an ADR that re-centers HK 2.0 on the HK 1.0 lifecycle.
- [x] Update the HK 2.0 design/spec language from generic ledger-first product to lifecycle-first CLI backed by a ledger.
- [x] Sketch staged implementation path for lifecycle aliases, validation rationale, review records, readiness, and handoff/export polish.
- [x] Update the target lifecycle shape to include `hk context` as the public context-engineering verb.
- [x] Capture questionnaire decisions and concerns about context, ceremony, one obvious way, and reshaping PR #12 before merge.
- [x] Write detailed lifecycle implementation plan with tasks, tests, validation, and open questions.
- [x] Add dogfood rollout plan using real harness-toolkit work, synthetic repos, and subagent review roles.

## Follow-up candidates

- Implement Slice 1: `hk start`, `hk status`, `hk context`, `hk plan`, and `hk decide` lifecycle facade.
- Implement Slice 2: `hk validate --why ... -- <command>`.
- Implement Slice 3: `hk review add`.
- Implement Slice 4: `hk ready`.
- Implement Slice 5: export/deprecation plan.
- Revisit profile vs `.harness/harness.toml` design; likely simplification is to make `.harness` the durable config model and treat profiles as presets/checksets or migration compatibility.
