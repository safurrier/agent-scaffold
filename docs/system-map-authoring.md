---
id: system-map-authoring
title: System Map Authoring
description: >
  How to write .harness/system.toml maps that give agents component ownership,
  must-preserve invariants, read-before-editing references, and relevant profile
  check labels without creating a second readiness system.
index:
  - id: purpose
    keywords: [system-map, system.toml, components, invariants]
  - id: invariant-semantics
    keywords: [must-preserve, conflict, superseded, decisions]
  - id: schema
    keywords: [toml, components, relations, validation_checks]
  - id: profile-integration
    keywords: [profiles, checks, reviews, readiness]
  - id: examples
    keywords: [examples, anti-patterns]
---

# System Map Authoring

System maps are compact pre-edit contracts for agents. They connect changed paths
to the component, invariants, docs, and profile check labels an agent should
consider before editing.

A repo-owned v1 file lives at:

```text
.harness/system.toml
```

For shared repos where personal agent guidance should not be committed, attach a target-level map from `harness.toml` instead:

```toml
[[targets]]
name = "discord-ads-relevance"
path = "~/discord"
profile = "discord-ai-ads-relevance"
system_map = "system-maps/discord-ads-relevance.toml"
```

Target-level maps are personal/user overlays. Paths inside the map are still repo-root-relative, not relative to the map file.

Resolution order is intentionally simple:

1. `system_map` on the matched target in `harness.toml`.
2. Repo-local `.harness/system.toml`.
3. No system map.

HK does not merge maps in v1. If both a target-level map and repo-local map exist, the target-level map wins and `hk brief` reports that it overrides `.harness/system.toml`.

A system map is not an architecture essay. It is a queryable contract that powers
`hk brief` and `hk checks --changed`. Use `hk config inspect` to see which map is
active, `hk config validate` to catch parse/reference/label problems,
`hk config explain --path PATH` to understand why a path matched components and
labels, and `hk config audit` for conservative drift/surprise diagnostics. These
commands are read-only; they do not infer architecture or make system-map labels
readiness-blocking.

## Purpose

Use a system map when a repo has component boundaries or invariants that agents
can easily violate while making local changes.

Profiles answer:

```text
path -> check/review guidance
```

System maps answer:

```text
path -> component/invariant/read-before-editing/relevant check labels
```

The split is intentional:

- profiles own commands, review policy, and readiness;
- system maps own component and invariant context.

## Invariant semantics

Invariants are normative. A touched invariant should be preserved unless an
explicit decision supersedes it.

When `hk checks --changed` surfaces an invariant, agents should treat it as:

```text
Must preserve unless explicitly superseded.
```

If the requested change, plan, or current diff contradicts a surfaced invariant,
do not silently implement around it. Use the invariant conflict protocol:

1. State the surfaced invariant and the requested change.
2. Stop and confirm whether the user intends to supersede the invariant unless
   the user already made that explicit.
3. If superseded, record a loud invariant-supersession decision with `hk decide --kind invariant-supersession` and update `system.toml`, related docs, or
   tests in the same change when practical.
4. If not superseded, adjust the implementation and tests to preserve the
   invariant.
5. If the invariant is high-risk, run or record a profile-owned review/check for
   that component.

System maps do not create readiness blockers directly. If a repo needs a hard
stop, put the required check or review in the selected profile.

## Superseding invariants loudly

Invariant supersession is allowed, but it must be impossible to miss in the HK
paper trail, review prompt, handoff, PR description source material, and commit
message guidance.

Use `hk decide --kind invariant-supersession`:

```bash
hk decide "Switch message sends to Discord default mention parsing" \
  --kind invariant-supersession \
  --invariant message-writes.mentions-safe-by-default \
  --previous "Message sends and replies include allowed_mentions={parse=[]} by default." \
  --replacement "Message sends omit allowed_mentions by default; explicit allow-list flags still constrain parsing." \
  --reason "User-requested mention UX change." \
  --doc .harness/system.toml \
  --doc README.md \
  --spec-impact updated
```

Required supersession packet:

- invariant id;
- previous invariant text;
- reason/rationale;
- replacement invariant or removal rationale;
- docs/system-map paths that must change;
- validation and review evidence through normal profile/HK flow;
- commit message trailer: `Supersedes-Invariant: <id>`.

`hk status`, `hk ready`, `hk summary`, `hk handoff`, and `hk review prompt` surface
recorded supersessions loudly. `hk ready` fails if listed repo-local docs/system-map
files are not changed in the current work. Absolute docs outside the repo are
allowed for target-level maps and stay visible in the paper trail, but HK cannot
verify their diff from the target repo.

## Schema

Minimal shape:

```toml
version = 1

[system]
name = "example"
summary = "Short description of the system."

[[components]]
id = "name-normalization"
title = "Name normalization"
kind = "domain-function"
paths = ["src/app.py"]
read_before_editing = ["docs/architecture.md"]
validation_checks = ["unit-tests"]

[[components.invariants]]
id = "stripped-non-empty"
statement = "Name normalization strips surrounding whitespace and rejects empty display names."
evidence = ["src/app.py", "tests/test_app.py"]
validation_checks = ["unit-tests"]
```

Rules:

- `version = 1` is mandatory.
- Paths are repo-root-relative in v1, even when the map file is a target-level map stored outside the repo.
- Component ids are globally unique and kebab-case.
- Invariant ids are unique within a component.
- The machine-facing invariant id is `<component-id>.<invariant-id>`.
- `validation_checks` contains profile check labels, not command templates.
- Relations must reference known component ids.

## Choosing components

Add a component only when it helps edit routing. A good component has at least
two of:

- distinct responsibility boundary;
- owned state, data, resource, protocol, lifecycle, or artifact;
- input/output messages, commands, events, side effects, or model artifacts;
- invariant future edits often violate;
- focused validation or profile review label;
- separate docs or domain vocabulary.

Avoid components that are arbitrary folders, generated code, vendored code, thin
wrappers, or obvious one-file utilities with no invariant.

## Writing good invariants

Good invariants are short, concrete, and testable:

```toml
[[components.invariants]]
id = "profiles-own-requiredness"
statement = "Profiles own check commands and required/suggested semantics; adjacent context layers must not create hidden readiness policy."
evidence = [
  "src/harness_toolkit/kit/profiles/models.py",
  "src/harness_toolkit/kit/profiles/applicability.py",
  "src/harness_toolkit/kit/readiness/policy.py",
]
validation_checks = ["focused-unit-tests", "hk-dev-dogfood"]
```

Weak invariants are vague, decorative, or unverifiable:

```toml
# Too vague.
statement = "The backend should be clean and maintainable."

# Too much prose.
statement = "Historically this module grew out of several design decisions and should probably continue to support most of the same usage patterns unless a future migration changes that direction."
```

## Profile integration

System-map check labels are relevant labels, not requiredness.

This is good:

```toml
validation_checks = ["unit-tests"]
```

This belongs in a profile, not the system map:

```toml
[[checks]]
name = "unit-tests"
purpose = "Run focused unit tests."
command_template = "uv run pytest"
run_from = "repo-root"
required_when = ["src/app.py"]
```

For high-risk invariants, add a profile-owned review:

```toml
[[reviews]]
name = "invariant-conflict-review"
purpose = "Review changes touching invariant-bearing components for preserved or explicitly superseded invariants."
backend = "codex"
applies_when = ["src/app.py"]
required_when = ["src/app.py"]

[reviews.instructions]
type = "inline"
text = "Review whether changed files preserve surfaced .harness/system.toml invariants. If an invariant is superseded, verify an explicit decision and system map/docs update."
```

## What `hk checks --changed` should communicate

Text output should make invariant semantics clear:

```text
System invariants for changed paths:
Policy: must preserve surfaced invariants unless the user explicitly supersedes them.
- name-normalization matched src/app.py.
  Must preserve name-normalization.stripped-non-empty: Name normalization strips surrounding whitespace and rejects empty display names.
  Relevant check labels: unit-tests
  Read before editing: docs/architecture.md
If the requested change contradicts an invariant, stop and resolve the conflict: confirm supersession with the user, record a decision, and update the system map/docs or run the required invariant review.
```

The JSON output remains advisory so tools do not mistake system maps for readiness
policy:

```json
{
  "system_context": {
    "advisory": true,
    "invariant_policy": "must_preserve_unless_superseded",
    "conflict_protocol": "stop_confirm_record_decision"
  }
}
```

## Anti-patterns

Do not use system maps for:

- command templates;
- setup instructions;
- generic workflow rules;
- readiness requiredness;
- directory tours;
- stale architecture history;
- broad claims without evidence.

If the useful guidance is only "run this command for these paths," put it in a
profile instead.
