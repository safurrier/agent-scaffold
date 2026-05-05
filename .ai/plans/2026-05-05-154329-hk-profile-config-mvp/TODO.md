---
id: plan-todo
title: Task List
description: >
  Checkable tasks for this unit of work. Check off as you go.
---

# TODO — hk-profile-config-mvp

- [x] Design and implement user-level `harness.toml` loading.
- [x] Parse inline `[profiles.<name>]` profile definitions.
- [x] Parse explicit `[[targets]]` path-to-profile bindings.
- [x] Parse lightweight `[[profiles.<name>.reviews]]` guidance, including optional prompt files.
- [x] Add `hk profile resolve --target PATH --json`.
- [x] Make `hk checks --target PATH` use resolved profile when `--profile` is omitted.
- [x] Add tests for config loading, profile override, target resolution, and checks defaulting.
- [x] Document user config/profile MVP and deferred `.harness/` layering.
- [x] Dogfood in temp clones for dread and foreman with sample user config.
- [x] Confirm Codex review backend guidance works or record friction.
- [x] Run focused tests, `mise run check`, and plan sync-check.
- [x] Obtain fresh-context review.
