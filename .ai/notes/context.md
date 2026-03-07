# docs/add-agents-md-context-files — Continuation Context

## Goal

Add AGENTS.md context files and docs frontmatter validation to agent-scaffold. The branch adds a proper AGENTS.md at repo root, a docs/AGENTS.md for generated project docs, frontmatter contract tests, and a test_docs.py template for generated Python repos.

## Current State

**Branch**: `docs/add-agents-md-context-files` (1 commit ahead of origin, unpushed)

**Commits on branch** (2 total):
1. `66642e5` — docs: add AGENTS.md and symlink CLAUDE.md to it
2. `b544d60` — feat: add docs frontmatter validation as pytest contract tests (unpushed)

**Untracked**: `.ai/notes/` (this file)

## What Was Done

- Created root `AGENTS.md` with WHY/WHAT/HOW structure, repo map, invariants, gotchas
- Symlinked `CLAUDE.md -> AGENTS.md` (so Claude Code picks it up)
- Added `docs/AGENTS.md` — lighter version for generated projects
- Removed frontmatter from `templates/AGENTS.md.tmpl` (AGENTS.md files don't get frontmatter, only docs/ files)
- Added `tests/_docs_helpers.py` — stdlib-only frontmatter parser (no pyyaml dependency)
- Added `tests/contract/test_docs_contract.py` — 34 contract tests for scaffold's own docs
- Added `stacks/python/tests/test_docs.py.tmpl` — generated repos get self-validating docs tests
- Updated `tests/unit/test_golden_output.py` with frontmatter assertions
- Updated `tests/contract/test_task_contract.py` with template existence check

## Key Files

| File | What |
|------|------|
| `AGENTS.md` | Root context file — WHY/WHAT/HOW structure |
| `CLAUDE.md` | Symlink to AGENTS.md |
| `docs/AGENTS.md` | Docs-specific context (for generated projects) |
| `tests/_docs_helpers.py` | Frontmatter parser + validators (stdlib only) |
| `tests/contract/test_docs_contract.py` | Contract tests for docs frontmatter |
| `stacks/python/tests/test_docs.py.tmpl` | Template for generated repo docs tests |
| `tests/unit/test_golden_output.py` | Golden output tests (updated with frontmatter) |
| `templates/AGENTS.md.tmpl` | AGENTS.md template for generated repos (frontmatter removed) |
| `docs/development.md` | Updated dev docs |

## What Likely Needs to Happen Next

1. **Run `mise run check`** to verify all tests pass with the latest commit
2. **Push** the unpushed commit to origin
3. **Open PR** for the branch
4. **Review**: Self-review the changes, check for anti-patterns
5. **Merge** once CI is green

## Vault Context

- Obsidian: `staging/agent scaffold.md` — Full SPEC.md (the design specification, exported from Claude Desktop)
- Obsidian: `staging/Skills + CLIs + Evals - Architectural Direction.md` — Broader context on how agent-scaffold fits into Leverage Eng work
- Obsidian: `Repo Registry.md` — Lists agent-scaffold as `safurrier/agent-scaffold`
- Obsidian: `.ai/notes/labels-evals-improvement-loops.md` — How agent-scaffold connects to the Labels > Evals > Improvement Loops framework
- Obsidian: `.ai/notes/leverage-eng-context.md` — How agent-scaffold maps to Leverage Engineering needs

## Reference Patterns

The docs frontmatter convention (from `docs/development.md` and the contract tests):

```yaml
---
id: kebab-case-id
title: Human-Readable Title
description: >
  One-line description of what this doc covers.
index:
  - id: section-id
    keywords: [keyword1, keyword2]
---
```

Tests validate: frontmatter presence, schema (id/title/description/index), uniqueness of ids, keywords on every index entry, mkdocs.yml nav consistency.

## Open Questions

- Are tests green? Need to run `mise run check` to verify.
- Any other docs that need frontmatter added/updated?
