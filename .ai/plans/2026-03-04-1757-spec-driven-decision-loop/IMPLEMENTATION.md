# Implementation Plan

## Phases 1-3: DONE

Architecture.md section tests, ADR schema tests, cross-reference integrity — all shipped. 297 tests passing, `mise run check` green. See LEARNING_LOG.md for details.

---

## Phase 4: SPEC.md Template

### 4.1 Create `templates/SPEC.md.tmpl`

6-section correctness envelope with frontmatter:

```yaml
---
id: {{project_name}}-spec
title: {{project_name}} Specification
description: >
  Correctness envelope — requirements, contracts, and invariants
  for {{project_name}}.
index:
  - id: requirements
    keywords: [must, should, may, behavioral, requirements]
  - id: interfaces
    keywords: [api, contracts, boundaries, modules, io]
  - id: invariants
    keywords: [state, safety, data, rules, boundaries, always-true]
---
```

Sections: Summary, Goals / Non-Goals, Requirements (MUST/SHOULD/MAY), Interfaces & Contracts, Invariants, Acceptance.

Each section has HTML comment guidance for how it scales (inline for small projects, routing index for large ones).

### 4.2 Contract tests for SPEC.md template

Add to `test_docs_contract.py`:
- `test_spec_template_exists`
- `test_spec_template_has_required_sections` (parametrized over 6 section names)
- `test_spec_template_has_frontmatter`

Define `SPEC_REQUIRED_SECTIONS` constant in `_docs_helpers.py`.

### 4.3 Golden output tests

Add to each of the 4 shape classes in `test_golden_output.py`:
- `test_spec_md_exists`
- `test_spec_md_has_frontmatter`
- `test_spec_md_has_required_sections`

---

## Phase 5: Rewrite Scaffold's Own SPEC.md

The current `SPEC.md` is a Claude Desktop export of the original design spec. Rewrite it to follow the 6-section template with real content:

- **Summary**: agent-scaffold is an opinionated starter repo...
- **Goals / Non-Goals**: from existing SPEC.md sections 1.1 and 1.2
- **Requirements**: distill from existing sections 2-6 into MUST/SHOULD/MAY
- **Interfaces & Contracts**: the 11-task contract, CLI interface, Stack Protocol
- **Invariants**: CI parity, golden path guarantee, worktree safety, stack dispatch via env
- **Acceptance**: `mise run check`, `mise run verify`, golden output tests

Add frontmatter with index entries. The existing SPEC.md content becomes the source material — condense, don't just copy.

---

## Phase 6: Architecture.md Template Update

Shift architecture.md to purely descriptive:

**Remove** (moved to SPEC.md):
- Invariants that are correctness rules (worktree safety, CI parity, etc.)
- Any MUST-style normative language

**Keep**:
- System Overview (components, data flows, trust boundaries)
- Goals / Non-Goals (can overlap with SPEC.md — architecture version is "what the system optimizes for")
- Principles & Preferred Patterns ("prefer X because Y" — guidance, not hard rules)
- Cross-Cutting Workflows (validation loop, artifact debugging)
- Decisions (ADR index + truth hierarchy)
- Module Map
- Where Human Thought Goes

**Add**:
- Cross-reference to SPEC.md at top: "For correctness invariants, see `SPEC.md`"

**Update** `ARCHITECTURE_REQUIRED_SECTIONS` constant if any sections are removed or renamed.

---

## Phase 7: AGENTS.md Template Update

In `templates/AGENTS.md.tmpl`:
- Add `SPEC.md` to the "Key steering files" list
- Add to the "Further Reading" table

In root `AGENTS.md`:
- Add SPEC.md to docs index

---

## Phase 8: Generated Repo Tests

Update `stacks/python/tests/test_docs.py.tmpl`:
- Add SPEC.md existence and section validation tests
- Keep existing architecture + ADR tests

Update E2E tests (`test_python.py`, `test_go.py`):
- `test_spec_md_exists` — verify SPEC.md generated after init
- `test_spec_md_has_frontmatter`

---

## Phase 9: ADRs From This Session

Create ADRs in `docs/decisions/` for the scaffold itself:

**0002-spec-as-correctness-envelope.md**: SPEC.md defines the correctness envelope (what must always be true), distinct from architecture.md (what IS true). Driven by Breunig's spec-driven development triangle and the need for a document that agents can read to understand the full set of constraints.

**0003-spec-six-section-structure.md**: SPEC.md uses 6 sections (Summary, Goals/Non-Goals, Requirements, Interfaces, Invariants, Acceptance). Distilled from NLSpec's 12 sections — dropped sections that are better in architecture.md or only needed for feature-level specs. Scales via progressive disclosure (inline for small, routing index for large).

**0004-architecture-descriptive-only.md**: Architecture.md shifts to descriptive content (principles, decisions, module map). Normative invariants move to SPEC.md. Clean separation: SPEC = what must be true (CI-enforceable), architecture = what IS true + guidance.

**0005-bottom-up-spec-maintenance.md**: Spec stays current by construction — decisions are extracted from PRs (agent-agnostic: diff + PR metadata), proposed as ADRs, approved as part of normal PR review. Groundskeeper skill chain as the implementation (follow-on work). Inspired by Breunig + labels/evals/loops framework.

Each ADR follows the template schema (Status, Date, Generated from, Context, Decision, Consequences, Alternatives) and is validated by the contract tests from Phases 1-3.

Update architecture.md decisions index table to list all new ADRs.

---

## Validation Plan

### Per-phase verification

| Phase | Verify with | Pass criteria |
|-------|------------|---------------|
| 4 (SPEC template) | `uv run pytest tests/contract/ tests/unit/test_golden_output.py -v` | SPEC.md template has sections + frontmatter; all shapes generate valid SPEC.md |
| 5 (own SPEC.md) | `uv run pytest tests/contract/test_docs_contract.py -v` | Scaffold's own SPEC.md passes section + frontmatter tests |
| 6 (architecture shift) | `uv run pytest tests/ -v` | All existing architecture tests pass with updated sections |
| 7 (AGENTS.md update) | `uv run pytest tests/ -v` | AGENTS.md tests still pass |
| 8 (generated tests) | `mise run check` | Full suite green including E2E |
| 9 (ADRs) | `uv run pytest tests/contract/ tests/unit/test_golden_output.py -v` | New ADRs pass schema validation |

### Final gate
`mise run check` — all tests pass, same command CI runs.
