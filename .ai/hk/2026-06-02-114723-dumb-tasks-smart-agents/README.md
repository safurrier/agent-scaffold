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
- Expanded docs PR to publish MkDocs, bump 0.3.0, reorganize docs into explanation/how-to/reference, refresh README positioning, and update validation contracts/links for the new layout.

## Plan
- Add a repo docs page explaining Harness Kit's what/why thesis, using harness-toolkit dogfood examples and wiring it into MkDocs.

## Decisions and spec reflection
- Added a product-philosophy docs page for HK's dumb tasks, smart agents thesis.
- Publish docs and reorganize repo docs by intent taxonomy.
  - Spec: not-needed: Spec/docs update not needed.
  - Spec: updated: Spec/docs updated or verified.; refs: docs/AGENTS.md, mkdocs.yml, CHANGELOG.md

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
- `uv run pytest -m contract`: pass (exit 0) — validates: Docs contract still passes after highlighting the main thesis. — `<local HK state not exported>`
- `uv run mkdocs build --strict`: pass (exit 0) — validates: MkDocs still builds after highlighting the main thesis. — `<local HK state not exported>`
- `uv run pytest -m contract`: pass (exit 0) — validates: Docs contract passes after adding sync to the smallest useful loop. — `<local HK state not exported>`
- `uv run mkdocs build --strict`: pass (exit 0) — validates: MkDocs builds after adding sync to the smallest useful loop. — `<local HK state not exported>`
- `uv run pytest -m contract`: pass (exit 0) — validates: Docs frontmatter, renamed docs paths, MkDocs navigation, and docs contract tests pass after intent-taxonomy migration. — `<local HK state not exported>`
- `uv run mkdocs build --strict`: pass (exit 0) — validates: MkDocs builds after docs folder migration and Pages workflow additions. — `<local HK state not exported>`
- `uv run python /Users/alex.furrier/.pi/agent/skills/context-engineering-context-docs/scripts/docs_verify.py .`: pass (exit 0) — validates: Context-docs structural verifier passes after docs folder migration. — `<local HK state not exported>`
- `mise run check`: fail (exit 1) — attempted to validate: Fast gate passes after version bump, docs IA migration, README refresh, and Pages workflow addition. — `<local HK state not exported>`
- `mise run check`: fail (exit 1) — attempted to validate: Fast gate passes after version bump, docs IA migration, README refresh, and Pages workflow addition. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Fast gate passes after version bump, docs IA migration, README refresh, Pages workflow addition, and version test update. — `<local HK state not exported>`
- `mise run verify`: pass (exit 0) — validates: Heavy gate passes for workflow and release/docs changes. — `<local HK state not exported>`
- `uv run pytest -m contract`: pass (exit 0) — validates: Docs contract passes after release-version and docs workflow review fixes. — `<local HK state not exported>`
- `uv run mkdocs build --strict`: pass (exit 0) — validates: MkDocs builds after release-version and docs workflow review fixes. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Fast gate passes after docs workflow, 0.3.0 release prep, docs migration, and review fixes. — `<local HK state not exported>`
- `mise run verify`: pass (exit 0) — validates: Heavy gate passes after final docs workflow and release-prep fixes. — `<local HK state not exported>`
- `mise run sync-check`: pass (exit 0) — validates: Committed HK handoff export validates after docs publishing and IA migration changes. — `<local HK state not exported>`

## Readiness
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:focused-contract-tests: pass — required profile check recorded: focused-contract-tests (matched docs/AGENTS.md, docs/explanation/ci.md, docs/explanation/harness-kit-lifecycle-design.md, +34 more)
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched AGENTS.md, README.md, docs/AGENTS.md, +43 more)
- profile-check:handoff-sync-check: pass — required profile check recorded: handoff-sync-check (matched .github/workflows/docs.yml)
- profile-check:heavy-gate: pass — required profile check recorded: heavy-gate (matched .github/workflows/docs.yml)
- profile-review:codex-review: pass — required profile review recorded: codex-review (matched AGENTS.md, docs/AGENTS.md, docs/explanation/ci.md, +39 more)

## Review
- subagent / reviewer-fresh-context [codex-review]: Fresh-context docs review found no blockers. It suggested qualifying profile/system-map examples as illustrative user-level dogfood config and using an unlabelled validate command in the smallest-loop example; both were applied and revalidated. paths: README.md, docs/AGENTS.md, docs/index.md, +2 more. [accepted]
- subagent / parent-agent [codex-review]: Targeted follow-up: highlighted the main thesis as a bold blockquote; no semantic changes. paths: docs/harness-kit-what-and-why.md. [accepted]
- subagent / parent-agent [codex-review]: Targeted follow-up: accepted Codex feedback and added hk sync before hk ready in the smallest useful loop; also updated the explanatory sentence. paths: docs/harness-kit-what-and-why.md. [accepted]
- subagent / reviewer-fresh-context [codex-review]: Fresh-context review of expanded docs publishing/restructure/release-prep slice found one blocker: stale v0.2.0 install/release references after 0.3.0 bump. It also suggested docs workflow path filters for pyproject/uv.lock and least-privilege permissions. All were fixed and revalidated. paths: AGENTS.md, CHANGELOG.md, README.md, +44 more. [accepted]
