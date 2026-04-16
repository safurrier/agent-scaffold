---
name: slice-implementer
description: >
  Implement a slice while keeping the active plan, validation log, and artifact
  manifest current.
allowed-tools: Read, Edit, Glob, Grep, Bash
---

Use this skill while coding a meaningful slice.

## Workflow

1. Follow the active plan's TODO order
2. Update `LEARNING_LOG.md` as surprises, pivots, or user corrections appear
3. Record commands and outcomes in `VALIDATION.md` as soon as they happen
4. Persist evidence into the plan's `artifacts/` directory instead of temp files
5. Update `artifacts/manifest.yaml` whenever a new proof artifact is created
6. Keep `DECISIONS.md` current if the change diverges from the planned design

## Rule

Treat validation and evidence as part of implementation output, not as cleanup
to remember later.
