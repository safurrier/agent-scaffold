# HK export: `2026-06-03-095104-scaffold-docs-workflow-cleanup`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-06-03-095104-scaffold-docs-workflow-cleanup --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-06-03-095104-scaffold-docs-workflow-cleanup`
- Branch: `fix/scaffold-docs-workflow-cleanup`

## Context
- harness-scaffold generated projects currently include docs/ and a mise docs task, but init removes the scaffold repo's mkdocs.yml and does not intentionally make MkDocs publishing first-class. The root .github/workflows/docs.yml added for harness-toolkit itself is accidentally retained in generated repos.

## Plan
- Stop harness-scaffold generated projects from accidentally inheriting the harness-toolkit MkDocs Pages workflow. Add a short Harness Toolkit docs note for enabling GitHub Pages after gh-pages deploy.

## Decisions and spec reflection
- Do not include the harness-toolkit GitHub Pages deploy workflow in generated repos until MkDocs is a deliberate scaffold feature.
  - Spec: updated: Spec/docs updated or verified.; refs: AGENTS.md, docs/how-to/release.md

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `uv run pytest tests/e2e/test_post_init_contract.py -q`: pass (exit 0) — validates: Scaffold post-init contract confirms generated Python projects keep CI but do not inherit docs.yml without mkdocs.yml; docs contract passes after Pages setup note. — `<local HK state not exported>`
- `uv run mkdocs build --strict`: pass (exit 0) — validates: MkDocs builds after adding GitHub Pages setup note. — `<local HK state not exported>`
- `uv run pytest -m contract`: pass (exit 0) — validates: Contract tests pass after scaffold cleanup and docs note. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Fast gate passes after removing accidental docs deploy workflow from scaffolded repos and documenting Pages enablement. — `<local HK state not exported>`
- `bash -lc 'uv run pytest tests/e2e/test_post_init_contract.py -k scaffolded_python_projects_do_not_inherit_pages_workflow -q && uv run mkdocs build --strict'`: pass (exit 0) — validates: Focused scaffold regression and MkDocs docs build pass after final Pages API command fix. — `<local HK state not exported>`

## Readiness
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:focused-contract-tests: pass — required profile check recorded: focused-contract-tests (matched docs/how-to/release.md)
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched AGENTS.md, docs/how-to/release.md, src/harness_toolkit/scaffold/init.py, +1 more)
- profile-review:codex-review: pass — required profile review recorded: codex-review (matched AGENTS.md, docs/how-to/release.md, src/harness_toolkit/scaffold/init.py, +1 more)

## Review
- subagent / reviewer-fresh-context [codex-review]: Fresh-context review confirmed cleanup_scaffold removes the root-only docs deploy workflow while generated ci.yml remains and regression coverage is appropriate. Reviewer found one blocker in the documented gh api command for Pages enablement; fixed by switching to bracketed source[branch]/source[path] fields and revalidated MkDocs plus the focused regression test. paths: AGENTS.md, docs/how-to/release.md, src/harness_toolkit/scaffold/init.py, +1 more. [accepted]
