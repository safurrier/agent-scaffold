---
id: plan-decisions
title: Decisions
description: >
  Decision log for this unit of work. Capture tradeoffs and rationale.
---

# Decisions — hk-profiles-module-split

## What Changed

- Split `profiles/__init__.py` into focused profile modules.
- Kept `profiles/__init__.py` as a re-export compatibility facade.

## Why

- Profile applicability and path rules are likely to keep evolving, so locality matters.
- The old module failed the deletion test: deleting it would not remove complexity, it would scatter config parsing, matching, and serialization knowledge across callers.
- Smaller modules make the profile module seam easier to test and navigate.

## Where Reflected

- `src/harness_toolkit/kit/profiles/__init__.py`
- `src/harness_toolkit/kit/profiles/applicability.py`
- `src/harness_toolkit/kit/profiles/catalog.py`
- `src/harness_toolkit/kit/profiles/config.py`
- `src/harness_toolkit/kit/profiles/guidance.py`
- `src/harness_toolkit/kit/profiles/loading.py`
- `src/harness_toolkit/kit/profiles/parser.py`
- `src/harness_toolkit/kit/profiles/serialization.py`
- `src/harness_toolkit/kit/profiles/templates.py`
- `src/harness_toolkit/kit/profiles/validation.py`

## 2026-05-08 — Keep a compatibility facade

- Decision: Leave public imports available from `harness_toolkit.kit.profiles` even though implementations moved.
- Rationale: Existing CLI/local code and tests import `ProfileCatalog`, `ProfileError`, `profile_names`, and private test helpers from the package root; preserving that seam keeps this a behavior-preserving refactor.
