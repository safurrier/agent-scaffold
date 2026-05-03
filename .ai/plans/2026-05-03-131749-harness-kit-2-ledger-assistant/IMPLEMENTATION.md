# Implementation Notes

## Production Code

- Added `src/harness_toolkit/kit/local.py` for Harness Kit 2.0 local assistant primitives:
  - state resolution/init;
  - read-only brief model and Markdown renderer;
  - work ledger creation and event append;
  - typed notes;
  - sync checkpoint/freshness checks;
  - command capture with built-in redaction;
  - evidence parsing/listing;
  - materialized work views;
  - handoff rendering;
  - optional local spec init/status/outline/promote dry-run.
- Extended `src/harness_toolkit/kit/cli.py` with additive 2.0 commands:
  - `hk brief`;
  - `hk init`;
  - `hk work start/status/materialize`;
  - `hk note`;
  - `hk sync`;
  - `hk capture`;
  - `hk evidence list`;
  - `hk handoff`;
  - `hk spec init/status/outline/promote`.

## Tests

- Added `tests/unit/test_harness_kit_2.py` for local assistant behavior.
- Added `tests/unit/test_script_contract_prototype.py` for script-contract prototype behavior.

## Docs

- Added `docs/harness-kit-2-design.md`.
- Added `docs/decisions/0008-harness-kit-2-ledger-first-local-assistant.md`.
- Added `docs/script-contract-prototype.md`.
- Updated README, SPEC, portable workflow docs, mkdocs nav, and docs routing index.

## Migration Posture

The new commands are additive in this pass. Current portable workflow commands remain available while the 2.0 model stabilizes.
