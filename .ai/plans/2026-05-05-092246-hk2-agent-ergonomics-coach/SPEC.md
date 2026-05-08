---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — hk2-agent-ergonomics-coach

## Problem

PR-sized dogfood showed that HK2's lifecycle is directionally right, but agents still miss or discover key lifecycle records late. The CLI should make the happy path more obvious without turning HK into a task runner or adding boilerplate ceremony.

Two user clarifications shape this slice:

- Slugs should be guided as short human-readable names; chronological ordering should come from HK-generated timestamps/work IDs, not from users manually encoding dates.
- `hk start --plan` should be a start-time convenience that records the first lifecycle plan event. Root `hk plan` should mean lifecycle plan recording for active HK2 work, while legacy artifact plan creation lives only under `hk legacy plan`.

## Requirements

### MUST

- Add `hk start <slug> --plan '...'` to create work and immediately record one lifecycle plan event.
- Add optional `hk start <slug> --context '...'` to seed one context record only when the user provides meaningful context.
- Keep slugs short and human-readable in docs/help; preserve chronological ordering through generated timestamps/work IDs.
- Make root `hk plan` lifecycle-only. Legacy plan artifact creation must be available only as `hk legacy plan <slug>`.
- Upgrade `hk status` into a preflight / next-action coach that reports active work and missing lifecycle pieces.
- Add `hk dangerously-skip sync --reason '...'` that records a dangerous skip, satisfies sync readiness, and renders prominently in handoff.
- Keep structured `--spec-ref` / docs reflection out of this implementation slice.
- Preserve shell-first validation: HK records native command evidence; it does not choose or run project validation commands automatically.
- Preserve review independence: same-agent self-review does not count.

### SHOULD

- Update help text and examples to prefer the new happy path:
  `hk start <slug> --plan '...'` → optional `hk context`/`--context` → `hk decide` → `hk validate` → `hk review add` → `hk sync`/`hk ready`/`hk handoff`.
- Make `hk status` useful both before implementation and before handoff.
- Mention `.pi`/agent-local sync state in status/ready guidance when relevant.
- Add focused unit/e2e coverage for the command shape and readiness semantics.
- Run a targeted three-worker PR-sized dogfood rerun after implementation.

## Constraints

- Do not read the forbidden Obsidian note: `<PRIVATE_VAULT_PATH> kit 2.0 refactor.md`.
- Do not reintroduce root `hk sync-check`; legacy sync-check stays under `hk legacy sync-check`.
- Do not silently ignore `.pi` or other agent-local state as part of sync freshness.
- Do not add fuzzy conversation parsing, `hk adopt`, or HK-mediated command execution.
- Keep changes compatible with the current `mise run check` and `mise run sync-check` repo gates.
