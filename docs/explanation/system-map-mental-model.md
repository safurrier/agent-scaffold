---
id: system-map-mental-model
title: System Map Mental Model
description: >
  How Harness Kit system maps complement profiles by adding component and
  invariant context to changed paths without owning validation policy.
index:
  - id: purpose
    keywords: [system-map, mental-model, profiles, invariants]
  - id: commands
    keywords: [brief, checks, changed, system_context]
  - id: target-level-maps
    keywords: [target-config, shared-repos, dots]
---

# System Map Mental Model

A system map is a compact pre-edit contract for agents.

Repo-owned maps live at:

```text
.harness/system.toml
```

Shared repos can instead use a target-level map from `harness.toml`:

```toml
[[targets]]
name = "discord-ads-relevance-model"
path = "~/git_repositories/discord/discord_ai/models/py/ads_relevance_v1"
profile = "discord-ads-relevance-model"
system_map = "system-maps/discord-ads-relevance-model.toml"
```

The point is simple:

> Before an agent edits code, HK can tell it: this path belongs to component X,
> these invariants matter, read these docs, and these profile check labels are
> relevant.

System maps also give HK a formal invariant conflict protocol:

> If the user intentionally changes a must-preserve invariant, record that as a
> loud supersession decision instead of quietly drifting the system contract.

```bash
hk decide --kind invariant-supersession ...
```

That supersession then appears in `hk status`, `hk ready`, `hk handoff`, and
review prompts.

## Profiles vs system maps

Before system maps, HK mostly knew:

```text
path -> profile checks/reviews
```

Profiles answer:

> What commands or reviews should I run?

System maps add:

```text
path -> component + invariant context
```

System maps answer:

> What am I touching, and what must I preserve?

This split is intentional. Profiles remain authoritative for commands,
requiredness, reviews, and readiness. System maps only reference existing profile
check labels as relevant context.

## How agents see it

`hk brief` tells an agent whether a system map exists and where it came from:

```bash
hk brief --target . --json
```

Example summary:

```json
{
  "system_map": {
    "source": "target-config",
    "path": ".../system-maps/foo.toml",
    "path_base": "repo-root",
    "status": "valid",
    "components": 3,
    "invariants": 6,
    "overrides": ".harness/system.toml"
  }
}
```

`hk checks --changed` matches the current diff against the map:

```bash
hk checks --target . --changed --json
```

Example context:

```json
{
  "system_context": {
    "source_kind": "target-config",
    "matched_components": [
      {
        "id": "message-writes",
        "invariants": [
          {
            "id": "mentions-safe-by-default",
            "statement": "Message sends suppress mention parsing by default."
          }
        ],
        "validation_checks": ["unit-tests"]
      }
    ],
    "invariant_policy": "must_preserve_unless_superseded",
    "conflict_protocol": "stop_confirm_record_decision"
  }
}
```

In text mode, HK summarizes the same idea:

```text
System invariants for changed paths:
Policy: must preserve surfaced invariants unless the user explicitly supersedes them.

- message-writes matched src/...
  Must preserve message-writes.mentions-safe-by-default: ...
  Relevant check labels: unit-tests

If the requested change contradicts an invariant, stop and resolve the conflict.
```

That is the main user-facing behavior: HK turns a changed path into component,
invariant, documentation, and validation-label context.

## Target-level maps for shared repos

Target-level maps are for repos where you want personal or team-local agent
context without committing it to the target repo.

For example, a `dots` config can own a Discord map:

```text
dots/config/harness-toolkit/system-maps/discord-ads-relevance-model.toml
```

The `system_map` value itself is resolved relative to `harness.toml`, but paths
inside the map are still relative to the target repo root:

```toml
paths = ["discord_ai/models/py/ads_relevance_v1/src/config"]
```

not:

```toml
paths = ["~/git_repositories/discord/discord_ai/models/py/ads_relevance_v1/src/config"]
```

HK resolves one active map in this order:

1. `system_map` on the matched target in `harness.toml`;
2. repo-local `.harness/system.toml`;
3. no system map.

HK does not merge maps in v1. If a target-level map exists, it wins and `hk
brief` reports the repo-local map as overridden.

## Superseding an invariant

Invariants are must-preserve unless explicitly superseded. When the requested
change intentionally contradicts an invariant, record it with `hk decide`:

```bash
hk decide "Switch message sends to Discord default mention parsing" \
  --kind invariant-supersession \
  --invariant message-writes.mentions-safe-by-default \
  --previous "Message sends suppress mention parsing by default." \
  --replacement "Message sends use Discord default mention parsing unless constrained." \
  --reason "User-requested UX change." \
  --doc .harness/system.toml \
  --spec-impact updated
```

HK records a commit trailer to carry into the final change:

```text
Supersedes-Invariant: message-writes.mentions-safe-by-default
```

The goal is not to block product changes. The goal is to make invariant changes
visible, reviewed, and easy to audit later.
