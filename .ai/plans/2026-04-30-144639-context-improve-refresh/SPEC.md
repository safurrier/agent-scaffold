---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — context-improve-refresh

## Problem

Run a lean context-improvement pass on agent-scaffold. Root `AGENTS.md` had
useful information but exceeded the repo-root context target, duplicated docs
site content, and referenced stack-specific docs too directly. The
context-engineering validator also found missing docs-routing entries and
several backticked generated-output paths that looked like broken current-repo
references.

## Requirements

### MUST

- Keep agent-scaffold's existing generated-repo contract intact.
- Keep root `AGENTS.md` focused on repo-wide rules, validated commands, gotchas,
  and routing pointers.
- Fix deterministic context validation failures without pretending generated
  output paths exist in the scaffold repo.
- Avoid committing local plugin checkout paths or absolute user-specific paths.
- Validate with context-engineering checks and the repo's own quality gate.

### SHOULD

- Prefer existing docs over new docs.
- Preserve useful generated-repo examples while making current-repo references
  machine-checkable.

## Constraints

- Do not change runtime or generated project behavior.
- Do not regenerate the docs tree; it already exists.
- No relevant prior session history was found by the context-engineering session
  scanner, so changes are based on repo inspection and deterministic validator
  output.
