# HK export: `2026-06-12-102439-profile-last-mile-guidance`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-06-12-102439-profile-last-mile-guidance --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-06-12-102439-profile-last-mile-guidance`
- Branch: `docs/hk-profile-last-mile-guidance`

## Context
- AGENTS-only product guidance update for HK profile semantics; no CLI behavior changes.

## Plan
- Document Harness Kit product boundary: use profile instructions and handoff/readiness notes for judgment-heavy last-mile workflow sequencing; do not encode PR/context/docs workflows as required checks.

## Decisions and spec reflection
- Document last-mile workflow guidance as profile instructions/check notes rather than required HK checks; product guidance only.
  - Spec: not-needed: Spec/docs update not needed.; refs: AGENTS.md

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `uv run pytest tests/contract/test_docs_contract.py -q`: pass (exit 0) — validates: Docs contract passes after AGENTS guidance update — `<local HK state not exported>`

## Readiness
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded

## Review
- codex / codex-cli: Codex review found no code or workflow-breaking issue for the AGENTS.md guidance-only diff. [accepted]
