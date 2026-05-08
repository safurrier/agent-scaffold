---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — hk-profiles-module-split

## Problem

`src/harness_toolkit/kit/profiles/__init__.py` grew into a shallow module that mixed the public facade, config loading, TOML parsing, applicability matching, serialization, and template rendering. That reduced locality for profile changes.

## Requirements

### MUST

- Preserve the public import surface of `harness_toolkit.kit.profiles`.
- Keep runtime behavior unchanged for profile resolution, `hk checks --changed`, named reviews, and gitignore-style path rules.
- Move cohesive profile implementation concerns into focused modules.
- Pass existing profile and portable workflow tests.

### SHOULD

- Keep new modules small and named after their responsibility.
- Avoid changing product behavior or docs beyond plan artifacts for this refactor.

## Constraints

- No new CLI behavior.
- No new profile schema fields.
