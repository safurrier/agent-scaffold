# HK export: `2026-05-13-102409-adr-review-freshness-docs`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-05-13-102409-adr-review-freshness-docs --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-05-13-102409-adr-review-freshness-docs`
- Branch: `adr-path-aware-review-freshness`
- Git SHA: `9c9440f`
- Dirty: `true`
- Sync status: `synced`

## Context
- Follow-up docs-only PR after PR #17. CI requires committed .ai/hk export for meaningful docs changes.

## Plan
- Record ADRs for compact HK export packages and path-aware review freshness, then link them from lifecycle docs/navigation.

## Decisions and spec reflection
- Record compact HK export and path-aware review freshness as ADRs instead of only vault/session notes because these are durable product decisions that explain current HK readiness behavior.
  - Spec: not-needed: Spec/docs update not needed.

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `mise run sync-check`: pass (exit 0) — validates: Existing HK handoff exports remain structurally valid while adding docs-only ADRs. — `<local HK state not exported>`
- `uv run pytest tests/contract/test_docs_contract.py -q`: pass (exit 0) — validates: Docs ADR frontmatter, nav entries, and ADR structure are valid. — `<local HK state not exported>`
- `uv run pytest tests/contract/test_docs_contract.py -q`: pass (exit 0) — validates: Docs ADR frontmatter, nav entries, ADR structure, and ID consistency are valid after final nit fix. — `<local HK state not exported>`
- `bash -lc 'uv run pytest tests/contract/test_docs_contract.py -q && mise run sync-check'`: pass (exit 0) — validates: Docs-only fast gate: ADR contract checks and current HK export sync-check pass; full hooks also ran on commit. — `<local HK state not exported>`

## Readiness
- Status: `ready-with-dangerous-skips`
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:focused-contract-tests: pass — required profile check recorded: focused-contract-tests (matched docs/decisions/0011-path-aware-review-freshness.md)
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched docs/decisions/0011-path-aware-review-freshness.md)
- profile-review:codex-review: pass — review dangerously skipped: codex-review; reason: Docs-only ADR follow-up PR; Codex-specific review is not necessary for the small documentation fix.; mitigation: Fresh-context docs subagent review found no blockers, docs contract tests passed, sync-check passed, and GitHub Devin review/CI will run on the PR.
- sync: pass — sync checkpoint fresh

## Review
- pi-subagent / reviewer-fresh-context (docs-adr-conventions): Fresh-context docs review found no blockers for ADR 0010 compact exports, ADR 0011 path-aware review freshness, docs nav/index updates, and lifecycle link. Non-blocking ID consistency nit was fixed before recording. paths: docs/decisions/0011-path-aware-review-freshness.md. [accepted]

## Dangerous skips
- review: codex-review — reason: Docs-only ADR follow-up PR; Codex-specific review is not necessary for the small documentation fix.; mitigation: Fresh-context docs subagent review found no blockers, docs contract tests passed, sync-check passed, and GitHub Devin review/CI will run on the PR.
