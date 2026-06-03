---
id: harness-toolkit-adr-0010
title: ADR 0010 — Compact HK Export Packages
description: >
  Defines HK handoff-dir exports as compact generated review packages rather
  than Markdown mirrors of every ledger event type.
index:
  - id: decision
    keywords: [hk, export, handoff, ledger, artifacts]
  - id: package-shape
    keywords: [README.md, meta.json, .ai/hk]
---

# ADR 0010: Compact HK Export Packages

**Status**: Accepted  
**Date**: 2026-05-12  
**Deciders**: Alex Furrier  
**Generated from**: pr  
**Origin**: PR #14 follow-up design discussion  
**Amends**: `docs/reference/decisions/0009-harness-kit-lifecycle-first-cli.md`

---

## Context

PR #14 made the Harness Toolkit repo HK-native: HK ledger state is now the
canonical lifecycle source for meaningful repo work, while committed `.ai/hk/`
directories are generated handoff exports.

The first `hk export --format handoff-dir` design generated one Markdown file per
major lifecycle concern:

```text
.ai/hk/<work-id>/
  AGENTS.md
  SUMMARY.md
  HANDOFF.md
  VALIDATION.md
  REVIEW.md
  DECISIONS.md
  META.json
  artifacts/
```

That shape was readable, but it risked recreating the old `.ai/plans` workflow
as generated Markdown. The file tree looked like a second source of truth: plan,
validation, review, decisions, and handoff each had their own file. Even if HK
wrote those files, future agents and humans could reasonably infer that the
workflow state lived in the Markdown tree.

HK's intended model is different:

```text
Canonical state:      HK ledger
Human projection:     generated handoff/review package
Machine projection:   generated freshness/integrity metadata
Optional evidence:    explicitly attached artifacts
```

The export should make work reviewable without becoming another ledger.

## Decision

Use a compact generated export package for `hk export --format handoff-dir`:

```text
.ai/hk/<work-id>/
  README.md
  meta.json
  artifacts/
    README.md
```

`README.md` is the single human-facing handoff/review projection. It renders the
plan, decisions, validation evidence, review records, readiness, risks, and next
steps from HK ledger state.

`meta.json` is the machine-facing freshness and integrity file. It stores fields
such as work id, git SHA, diff hash, event/evidence counts, output path, file
list, and generated file hashes. Humans should only need to inspect it when a
freshness check fails.

`artifacts/` is explicit-only. HK does not automatically copy raw transcripts,
agent sessions, or bulky scratch files into committed exports. Durable artifacts
should be attached intentionally and kept reviewable. Export artifact payloads are
ignored by default except for small index files such as `artifacts/README.md` or
`artifacts/manifest.json`.

## Consequences

### Positive

- Keeps HK ledger state canonical and avoids a second Markdown workflow tree.
- Gives reviewers one obvious entry point: `README.md`.
- Keeps machine concerns in lowercase `meta.json` instead of a human-facing
  `META.json` convention.
- Makes artifact inclusion intentional, reducing the chance that `.ai/hk/` turns
  into a transcript or scratch-file dump.
- Makes future integrations simpler: tools can open `README.md` for humans and
  read `meta.json` for freshness/integrity.

### Negative / Trade-offs

- `README.md` can become long for work items with many validation or review
  records.
- Reviewers who want a standalone validation or review appendix do not get one by
  default.
- Existing exports from the first PR #14 implementation shape must be regenerated
  or cleaned up.
- The CLI format name `handoff-dir` is still acceptable but not perfect: the
  output is now more of a compact handoff package than a directory of separate
  handoff subdocuments.

### Guardrails

Future export changes should preserve the projection boundary:

- Do not add one default file per ledger event type.
- Do not make HK read generated Markdown back as state.
- Do not require humans to edit export files.
- Do not automatically attach latest agent sessions or raw transcripts.
- Prefer optional, evidence-oriented appendices only when `README.md` becomes too
  large for practical review.

## Alternatives considered

### Keep separate lifecycle Markdown files

Rejected. It is organized, but it recreates `.ai/plans` as generated files and
blurs the source-of-truth boundary.

### Add `PLAN.md` as a first-class file

Rejected. The plan is important, but making it a default file pushes the export
back toward a ledger mirror. The plan should render as a section of `README.md`.

### Rename `handoff-dir`

Deferred. Names such as `handoff-package` or `review-package` may be more exact,
but `handoff-dir` is already documented and still describes a directory export for
handoff. The package shape matters more than renaming the format in this change.

## Related

- PR #14: Make Harness Toolkit workflow HK-native
- `SPEC.md` HK export view invariant
- `docs/explanation/portable-workflow.md` HK export command reference
- `docs/reference/decisions/0008-harness-kit-ledger-first-local-assistant.md`
- `docs/reference/decisions/0009-harness-kit-lifecycle-first-cli.md`
