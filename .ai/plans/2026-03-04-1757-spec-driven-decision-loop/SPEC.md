# Spec-Driven Decision Loop

## Problem

agent-scaffold generates repos with `docs/architecture.md` and `docs/decisions/`, but:

1. **No SPEC.md** — There's no document defining the correctness envelope (what must be true about any valid implementation). Architecture.md mixes normative invariants with descriptive system state. The scaffold's own SPEC.md is a design doc from Claude Desktop, not a living spec.

2. **No structural enforcement** — Architecture.md and ADR templates have required sections from the AI Native Engineering RFC, but contract tests only checked "has frontmatter." *(Phases 1-3 now address this — section + ADR schema validation shipped.)*

3. **No feedback loop** — Specs drift because implementation decisions don't flow back. Breunig's "Spec-Driven Development Triangle" identifies this as the core failure mode. The bottom-up fix: decisions accumulate into the spec as a byproduct of the merge flow.

4. **Decisions are lost** — Architectural choices made during agent sessions live in conversation transcripts and die when sessions end. The diff shows *what*; the rationale is gone.

## Goal

1. Add a SPEC.md template to generated repos — 6-section correctness envelope that scales from CLI tools to large projects.
2. Rewrite the scaffold's own SPEC.md to follow the template (eat our own cooking).
3. Shift architecture.md to be purely descriptive — invariants move to SPEC.md.
4. Enforce SPEC.md structure with contract tests (same proven pattern).
5. Capture decisions from this session as ADRs (prove the decision loop works).

## Requirements

### MUST
- SPEC.md template with 6 sections: Summary, Goals/Non-Goals, Requirements (MUST/SHOULD/MAY), Interfaces & Contracts, Invariants, Acceptance
- SPEC.md template has machine-readable frontmatter with index entries
- Contract tests validate SPEC.md section structure in templates
- Golden output tests verify SPEC.md is generated for all 4 shapes
- Generated repos self-validate their SPEC.md via `test_docs.py.tmpl`
- Scaffold's own SPEC.md rewritten to follow the template
- Architecture.md template updated: remove normative invariants (now in SPEC.md), keep descriptive content
- ADRs created for key decisions from this design session

### SHOULD
- Architecture.md decision index cross-references validated (done in Phase 3)
- ADR `generated-from` field for traceability (done in Phase 2)

### Won't Have (This Plan)
- Groundskeeper decision extraction workflow (follow-on)
- Agent session trace parsing (follow-on)
- Module-level SPEC.md for apps-shape (future — start with root-level only)

## Constraints

- stdlib-only for test helpers (no pyyaml)
- No dependency on nlspec-factory — just opinionated markdown
- Don't break existing tests — extend them
- Contract tests must be fast (no subprocess)

## Context

### The Doc Split

| Doc | What | Changes when |
|---|---|---|
| **SPEC.md** | Correctness envelope — what must be true | Intent changes or new invariants discovered (via ADR) |
| **AGENTS.md** | How to work here — commands, repo map | Workflow or tooling changes |
| **docs/architecture.md** | System description — principles, decisions, module map | Continuously, as decisions accumulate |
| **docs/decisions/** | Individual choices | Created per-PR |

### Key Design Decisions (to be captured as ADRs)
- SPEC.md is a correctness envelope, not a design doc or implementation plan
- 6 sections chosen for scaling: small projects fill them inline, large projects use them as routing indexes
- Invariants define what must always be true; requirements define behavioral MUST/SHOULD/MAY
- "Can CI prove or falsify it?" is the heuristic for strong invariants vs guidance
- Architecture.md becomes descriptive only — principles stay there, invariants move to SPEC.md
- Agent-agnostic decision extraction: git diff + PR metadata as universal baseline

### Inspiration
- Drew Breunig, "The Spec-Driven Development Triangle" (2026-03-04)
- StrongDM Attractor NLSpec format (12 sections → distilled to 6 for repo-level use)
- "Enforce Invariants, Not Implementations" pattern
- Labels > Evals > Improvement Loops framework

## Future Work: Groundskeeper Decision Extraction

After this plan ships, the Groundskeeper workflow becomes viable:

- **Trigger**: Pre-merge (PR review is already a human decision point)
- **Inputs**: Git diff + PR metadata (universal), agent session traces (optional enrichment)
- **Process**: Extract decisions → propose ADRs conforming to the tested schema
- **Output**: ADR files + architecture.md index update added to PR branch
- **Validation**: `mise run check` enforces contract tests on proposed ADRs
- **Approval**: Human reviews decisions as part of normal PR review. Merge = approval.
