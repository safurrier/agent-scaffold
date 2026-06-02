# HK export: `2026-06-02-114723-dumb-tasks-smart-agents`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-06-02-114723-dumb-tasks-smart-agents --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-06-02-114723-dumb-tasks-smart-agents`
- Branch: `docs/dumb-tasks-smart-agents`

## Context
- None recorded.

## Plan
- Add a repo docs page explaining Harness Kit's what/why thesis, using harness-toolkit dogfood examples and wiring it into MkDocs.

## Decisions and spec reflection
- Added a product-philosophy docs page for HK's dumb tasks, smart agents thesis.
  - Spec: not-needed: Spec/docs update not needed.

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `uv run pytest -m contract`: pass (exit 0) — validates: Docs frontmatter and MkDocs navigation contract pass for the new Harness Kit what/why page. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Fast gate passes after adding the Harness Kit what/why doc and MkDocs navigation. — `<local HK state not exported>`
- `uv run mkdocs build --strict`: fail (exit 1) — attempted to validate: MkDocs builds with the new Harness Kit what/why page in nav. — `<local HK state not exported>`
- `uv run mkdocs build --strict`: pass (exit 0) — validates: MkDocs builds with the new Harness Kit what/why page in nav. — `<local HK state not exported>`
- `uv run pytest -m contract`: pass (exit 0) — validates: Docs frontmatter and MkDocs navigation contract pass after fixing the nav title. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Fast gate passes after final docs and MkDocs nav updates. — `<local HK state not exported>`
- `uv run pytest -m contract`: pass (exit 0) — validates: Docs frontmatter and MkDocs navigation contract pass after review fixes. — `<local HK state not exported>`
- `uv run mkdocs build --strict`: pass (exit 0) — validates: MkDocs builds after review fixes. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Fast gate passes after review fixes. — `<local HK state not exported>`
- `mise run sync-check`: pass (exit 0) — validates: Committed HK handoff export validates for this docs PR. — `<local HK state not exported>`
- `mise run sync-check`: pass (exit 0) — validates: Regenerated HK handoff export validates after recording sync-check evidence. — `<local HK state not exported>`

## Readiness
- context: info — no context recorded; okay for trivial work, add hk context if it prevents rediscovery
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:focused-contract-tests: pass — required profile check recorded: focused-contract-tests (matched docs/AGENTS.md, docs/index.md, mkdocs.yml, +1 more)
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched README.md, docs/AGENTS.md, docs/index.md, +2 more)
- profile-review:codex-review: pass — required profile review recorded: codex-review (matched docs/AGENTS.md, docs/index.md, docs/harness-kit-what-and-why.md)

## Review
- subagent / reviewer-fresh-context [codex-review]: Fresh-context docs review found no blockers. It suggested qualifying profile/system-map examples as illustrative user-level dogfood config and using an unlabelled validate command in the smallest-loop example; both were applied and revalidated. paths: README.md, docs/AGENTS.md, docs/index.md, +2 more. [accepted]
