---
id: profile-authoring
title: Profile Authoring
description: >
  How to write Harness Kit profiles that guide agents through focused iteration,
  final closeout gates, and targeted post-review follow-up without creating
  validation or review loops.
index:
  - id: lifecycle-roles
    keywords: [profiles, checks, iteration, closeout, validation]
  - id: required-vs-suggested
    keywords: [required_when, applies_when, readiness]
  - id: system-map-invariant-reviews
    keywords: [system-map, invariants, reviews, required_when]
  - id: reviews
    keywords: [reviews, targeted, advisory, follow-up]
  - id: examples
    keywords: [toml, fast-gate, handoff]
---

# Profile Authoring

Profiles are small workflow contracts. They tell agents which native commands and
independent reviews are relevant for a repo or module. They do **not** run those
commands, choose commands heuristically, or turn HK into a task runner.

Use `hk config inspect`, `hk config validate`, `hk config explain`, and
`hk config audit` to check deterministic profile/config joins while authoring or
maintaining profiles. These commands are read-only diagnostics. They can catch
missing target bindings, broken prompt files, unresolved system-map labels, and
path-rule explanations, but they do not infer the correct validation contract or
write profile TOML for you.

A good profile helps an agent avoid two failures:

1. under-validating a risky change; and
2. over-validating by rerunning broad checks and reviews after every small edit.

The second failure is a real closeout-loop risk. A profile should make the
intended cadence explicit.

## Lifecycle roles for checks

Classify checks by how agents should use them.

| Role | Purpose | Typical profile shape |
|---|---|---|
| Iteration check | Fast feedback while changing code. | Focused test selector, lint for touched area, small smoke. Usually `applies_when`; sometimes required for critical paths. |
| Final gate | Broad local confidence before commit/handoff. | `mise run check`, full unit suite, repo quality gate. Required for meaningful source/config/doc paths, but not usually `required_when = ["*"]`. |
| CI/heavy parity | Expensive merge, release, Docker, generated-project, or runtime parity. | Optional or path-specific `required_when` for CI/config/runtime-sensitive paths. |
| Apply/drift check | Apply generated config or detect drift after source/template changes. | Path-specific `applies_when` / `required_when`. |
| Handoff check | Verify HK/export evidence, not source behavior. | `mise run sync-check`, `hk sync && hk ready`; do not use this as a substitute for native validation. |

Write the profile `instructions` so the cadence is obvious:

```toml
instructions = "Use focused checks while iterating. Do not chase final readiness after every edit. Run broad final gates once implementation is stable and before handoff. After small review fixes, prefer targeted validation/review for changed paths unless behavior or design changed."
```

## `applies_when` vs `required_when`

Use `applies_when` for suggestions. Use `required_when` only when readiness should
block until the named evidence exists for matching paths.

Avoid broad expensive requirements like this unless the command is genuinely
cheap and must cover every changed path:

```toml
required_when = ["*"]
```

Prefer explicit path surfaces:

```toml
[[checks]]
name = "fast-gate"
purpose = "Default final quality gate before commit or handoff; not the inner-loop check."
command_template = "mise run check"
run_from = "repo-root"
applies_when = ["*"]
required_when = [
  "src/**",
  "tests/**",
  "docs/**",
  ".github/**",
  ".mise/**",
  "README.md",
  "SPEC.md",
  "pyproject.toml",
]
notes = [
  "Use focused checks while iterating.",
  "Run this once implementation is stable and before commit/handoff.",
]
```

Generated handoff packages such as `.ai/hk/**` should normally be covered by a
handoff/export check, not by a broad source validation gate:

```toml
[[checks]]
name = "handoff-sync-check"
purpose = "Validate generated HK handoff exports."
command_template = "mise run sync-check"
run_from = "repo-root"
applies_when = [".ai/hk/**", ".mise/tasks/sync-check", ".github/**"]
required_when = [".ai/hk/**", ".mise/tasks/sync-check", ".github/**"]
```

## System-map invariant reviews

When a repo has `.harness/system.toml`, use profiles to decide when invariant
context becomes blocking evidence. System maps explain components and invariants;
profiles own required checks and reviews.

For high-risk invariant-bearing paths, add a required review that checks whether
surfaced invariants were preserved or explicitly superseded:

```toml
[[reviews]]
name = "invariant-conflict-review"
purpose = "Review changes touching invariant-bearing components for preserved or explicitly superseded invariants."
backend = "codex"
applies_when = ["src/app.py"]
required_when = ["src/app.py"]

[reviews.instructions]
type = "inline"
text = "Review whether changed files preserve surfaced .harness/system.toml invariants. If an invariant is superseded, verify an explicit `hk decide --kind invariant-supersession` record, commit/PR callout, and system map/docs update."
```

Do not duplicate invariant statements into the profile. Let `hk checks --changed`
surface the invariant from the system map, and let the profile require the review
or validation evidence.

## Review policies

Profile reviews can be suggested or required. Keep required reviews
risk-specific and use suggested reviews for optional polish.

Required review guidance should say when to run a broad review and how to handle
small follow-up fixes:

```toml
[[reviews]]
name = "lifecycle-review"
purpose = "Focused independent review for lifecycle/readiness behavior."
backend = "subagent"
dispatch_hint = "Run near handoff after implementation stabilizes. For small later fixes, prefer targeted follow-up review for changed paths instead of rerunning the full broad review."
applies_when = ["src/harness_toolkit/kit/**", "docs/portable-workflow.md"]
required_when = ["src/harness_toolkit/kit/**"]

[reviews.instructions]
type = "inline"
text = "Review lifecycle safety, evidence freshness, review semantics, and whether HK stays guidance/evidence rather than a task runner."
```

Advisory reviews should be bounded:

```toml
[[reviews]]
name = "architecture-polish-review"
purpose = "Suggested final architecture/code-quality polish pass once implementation is stable and before handoff."
backend = "subagent"
dispatch_hint = "Run near handoff after focused validation. If it finds concrete fixes, implement the highest-leverage fixes and repeat at most one more time. Stop after 2 total passes or once stable. Do not run this mid-implementation."
applies_when = ["*"]
required_when = []
```

## Targeted post-review follow-up

HK records path/content coverage for reviews. If a broad review has already run
and a later fix touches only a small set of files, prefer targeted follow-up:

```bash
hk review add --review lifecycle-review \
  --path src/harness_toolkit/kit/local.py \
  --path tests/unit/test_harness_kit_2.py \
  --backend subagent \
  --reviewer lifecycle-reviewer \
  --summary "Targeted follow-up found no blockers."
```

Do not rerun the whole review stack unless the fix changes the main design,
behavior, or risk profile.

## Authoring checklist

Before installing or committing a profile, check:

- Does it name at least one focused iteration check when the repo has one?
- Are broad gates described as final closeout gates rather than inner-loop checks?
- Are expensive `required_when = ["*"]` entries avoided or explicitly justified?
- Are generated handoff/export paths covered by handoff checks instead of source gates?
- Are required reviews tied to concrete risk paths?
- Are advisory reviews bounded to one near-handoff pass plus at most one follow-up?
- Do instructions tell agents not to chase final readiness after every edit?

See [Profile Reviews](profile-reviews.md) for the review schema and
[Portable Workflow](portable-workflow.md) for profile discovery and target
resolution.
