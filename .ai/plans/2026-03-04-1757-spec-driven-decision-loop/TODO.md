# TODO

## Completed

### Phase 1: Architecture.md Section Contract Tests
- [x] Add `parse_sections()` and `find_section()` to `_docs_helpers.py`
- [x] Define `ARCHITECTURE_REQUIRED_SECTIONS` constant
- [x] Add `test_architecture_has_required_sections`
- [x] Add `test_architecture_invariants_section_nonempty`
- [x] Add `test_architecture_decisions_has_truth_hierarchy`
- [x] Add `test_architecture_decisions_index_table_exists`
- [x] Update golden output tests for architecture section checks

### Phase 2: ADR Schema Contract Tests
- [x] Add `ADRMetadata` dataclass and `parse_adr()` / `validate_adr()` to helpers
- [x] Define `ALLOWED_ADR_STATUSES`
- [x] Add `test_adr_has_valid_status` (via `validate_adr` in golden output)
- [x] Add `test_adr_has_required_sections` (Context, Decision, Consequences)
- [x] Add `test_adr_frontmatter_valid`
- [x] Add `generated-from` field to ADR template
- [x] Add `test_adr_has_generated_from` in golden output

### Phase 3: Cross-Reference Integrity
- [x] Add `test_architecture_decisions_index` in golden output
- [x] Add `derive_decisions_index()` helper

### Verification
- [x] `mise run check` green (297 tests, all passing)

---

## Phase 4: SPEC.md Template
- [ ] Create `templates/SPEC.md.tmpl` — 6-section correctness envelope with frontmatter
- [ ] Add contract tests for SPEC.md template (required sections, frontmatter)
- [ ] Add golden output tests for SPEC.md in all 4 shapes
- [ ] Verify: `uv run pytest tests/contract/ tests/unit/test_golden_output.py -v`

## Phase 5: Rewrite Scaffold's Own SPEC.md
- [ ] Rewrite root `SPEC.md` to follow the 6-section format
- [ ] Add frontmatter with index entries
- [ ] Fill in real content (not stubs): summary, goals, requirements, interfaces, invariants, acceptance
- [ ] Verify: contract tests pass on scaffold's own SPEC.md

## Phase 6: Architecture.md Template Update
- [ ] Remove normative invariants from `templates/docs/architecture.md.tmpl` (moved to SPEC.md)
- [ ] Keep: System Overview, Goals/Non-Goals, Principles, Workflows, Decisions, Module Map, Where Human Thought Goes
- [ ] Update `ARCHITECTURE_REQUIRED_SECTIONS` constant if sections change
- [ ] Add cross-reference to SPEC.md in architecture template
- [ ] Verify: all existing architecture contract + golden output tests still pass

## Phase 7: AGENTS.md Template Update
- [ ] Add SPEC.md to key steering files list in `templates/AGENTS.md.tmpl`
- [ ] Add SPEC.md to root `AGENTS.md` docs index
- [ ] Verify: existing AGENTS.md tests still pass

## Phase 8: Generated Repo Tests
- [x] Update `stacks/python/tests/test_docs.py.tmpl` with SPEC.md + architecture + ADR tests
- [x] Update E2E tests to verify SPEC.md exists and has sections after init
- [x] Ship all 3 skills to `templates/.agent/skills/` so generated repos include them
- [x] Verified: init → setup → check passes on fresh generated project with skills
- [x] Verify: `mise run check` (full suite) — 322 passed

## Phase 9: ADRs From This Session
- [x] ADR 0001: Single ADR covering all branch decisions (one-per-branch granularity)
  - SPEC.md as correctness envelope, 6-section structure, bottom-up maintenance, pre-push skills
  - Decided against splitting into 4 separate ADRs — one per branch is sufficient for this repo
- [x] Verify: ADR contract tests pass

## Final Gate
- [x] `mise run check` green (322 tests)
- [x] Ran pre-push skills — found and fixed: stale Stack Protocol, 11→12 task count, missing stacks, 6 docs gaps
- [x] Push, open PR: https://github.com/safurrier/agent-scaffold/pull/1

## Follow-on (Not This Branch)
- [ ] Groundskeeper skill: decision extraction from diff + PR metadata
- [ ] Agent session trace parsing (Claude Code JSONL, extensible to others)
- [ ] Module-level SPEC.md for apps-shape repos
- [ ] Blog post: "Working Backwards from Decisions" (labels/evals/loops angle)
