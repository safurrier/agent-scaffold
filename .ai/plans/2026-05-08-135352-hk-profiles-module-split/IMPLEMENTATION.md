---
id: plan-implementation
title: Implementation Notes
description: >
  Notes about the implementation approach and changed files.
---

# Implementation — hk-profiles-module-split

## Module split

- `guidance.py`: profile selection guidance text.
- `validation.py`: profile/check/review identifier validation.
- `parser.py`: profile TOML parsing and profile file loading.
- `config.py`: user-level `harness.toml` path/config/profile loading.
- `loading.py`: catalog assembly and profile lookup helpers.
- `applicability.py`: gitignore-style path matching, matched paths, suggestions, and `checks_view`.
- `serialization.py`: JSON serializers and prompt-file text redaction.
- `templates.py`: editable profile TOML template generation.
- `catalog.py`: `ProfileCatalog` facade over the focused modules.
- `__init__.py`: compatibility re-export surface.

## Notes

The first test run caught a missing compatibility export for `ProfileError`; the facade now re-exports the model types that callers previously got from the package root.
