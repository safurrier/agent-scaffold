# Learning Log — Spec-Driven Decision Loop

**Plan**: Harden docs standards, add SPEC.md as correctness envelope, enable bottom-up spec maintenance.

---

## Research Phase (2026-03-04)

### Breunig Article Discovery

Drew Breunig's "The Spec-Driven Development Triangle" (2026-03-04) provided the framing:
- Spec-driven development is a triangle (spec/tests/code), not linear
- Specs improve *through* implementation — pure planning misses gaps
- The real engineering task is keeping the three in sync
- Plumb CLI: extracts decisions from diffs + agent conversation traces

### Key Insight: Bottom-Up Spec Maintenance

Traditional top-down approach fails: write spec → implement → manually update when it drifts (update never happens).

Bottom-up: decisions accumulate into the spec as a byproduct of the merge flow. Architecture.md becomes a *living record* of approved decisions.

Maps to Labels > Evals > Improvement Loops: decisions as labels, contract tests as evals, spec updates as the loop.

### Agent-Agnostic Design Decision

Initially considered building on Claude Code JSONL session traces. User correctly identified this as too narrow. Decision:
- Universal baseline: git diff + PR description + PR comments
- Optional enrichment: agent session traces (any agent)
- Conversation traces are richest for *why*, but workflow can't depend on them

### Trigger Point: Before Merge

Human approval is already baked into PR merge. Don't add separate decision approval — surface extracted decisions as part of the PR. Merge = approval of both code and decisions. Same principle as "labels should be byproducts."

---

## Implementation Phase 1-3 (2026-03-04)

### What Was Built
- `_docs_helpers.py`: +193 lines — section parsing, ADR schema validation, `derive_decisions_index()`
- `test_docs_contract.py`: +78 lines — 7 new contract tests for architecture + ADR templates
- `test_golden_output.py`: +76 lines — 11 new golden tests across all 4 shapes
- ADR template: added `**Generated from**: init` traceability field
- Test count: 72 → 96 (contract + golden), 297 total suite

### What Went Smoothly
- Section parsing with regex worked cleanly — same stdlib-only pattern as frontmatter parser
- All existing architecture.md and ADR templates already had the right sections — no template changes needed (except generated-from field)
- Tests passed first run after formatting fixes

### Formatting/Lint Issues (Expected)
- `ruff format` caught two files
- `ruff check` caught 4 unused imports (imported helpers used only in golden output, not contract tests) + 1 import ordering
- Fixed in one pass with `mise run fmt` + `ruff check --fix`
- Lesson reinforced: run `mise run check` (not just pytest) during TDD

---

## Design Phase: SPEC.md (2026-03-04 → 2026-03-07)

### The Three-Doc Problem

Started with "architecture.md is the spec." Through discussion, realized architecture.md was serving two roles:
1. **Normative**: what must always be true (invariants, boundaries)
2. **Descriptive**: what the system looks like now (principles, decisions, module map)

These should be separate documents because they change at different rates and serve different audiences.

### NLSpec as Starting Point

Looked at the nlspec-factory plugin (Attractor-inspired, 12 required sections). Too heavy for a repo-level template — most sections would be empty stubs for a fresh project.

### Distilling to 6 Sections

User pushed for minimal sections that actually scale. Process:
1. Listed all sections across NLSpec (12), architecture.md (8), invariants doc (5)
2. Categorized each: is it SPEC territory, architecture territory, or AGENTS.md territory?
3. Collapsed related sections (data shapes + state rules + safety → single "Invariants" section)
4. Dropped sections only needed for feature-level specs (Glossary, Problem/Motivation, References)
5. Landed on 6: Summary, Goals/Non-Goals, Requirements, Interfaces & Contracts, Invariants, Acceptance

Key heuristic from user: "Can CI prove or falsify it?" → SPEC.md. If not → architecture.md (guidance) or AGENTS.md (workflow).

### Progressive Disclosure in Templates

User asked how to make templates scale. Considered `detail: inline` / `detail: docs/path.md` frontmatter tracking — rejected as over-engineering. Settled on:
- HTML comments in template explain how each section scales
- Frontmatter index entries provide machine-readable discovery
- Small projects: fill sections inline. Large projects: sections become routing indexes.

### The Clean Split

| Doc | What must be true | What IS true | How to work |
|-----|-------------------|--------------|-------------|
| SPEC.md | yes | | |
| architecture.md | | yes | |
| AGENTS.md | | | yes |

### Eating Our Own Cooking

User insisted on:
1. Rewriting scaffold's own SPEC.md to follow the template
2. Creating ADRs for decisions made during this design session
3. Validating everything with the contract tests we built

This proves the decision loop works — decisions from this conversation become ADRs that are validated by the contract tests we shipped in Phases 1-3.

---

## Problems Encountered

*(To be filled during Phases 4-9 implementation)*

## What Matched vs Diverged

*(To be filled on completion)*

## What Would Enable One-Shot Execution

*(To be filled on completion)*
