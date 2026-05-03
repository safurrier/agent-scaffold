# Validation

## Commands

```bash
uv run pytest -m contract
```

Result: passed — 255 tests.

```bash
uv run pytest tests/unit/test_harness_kit_2.py -q
```

Result: passed — 8 tests.

```bash
uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_script_contract_prototype.py -q
```

Result: passed — 10 tests.

```bash
uv run pytest -m "not slow"
```

Result: passed — 599 tests before script-prototype tests were added.

```bash
mise run check
```

Result: passed — format, lint, typecheck, and full non-slow test gate. Final captured evidence recorded in local Harness Kit 2 ledger:

```text
.harness-local/harness-kit/root/work/2026-05-03-132345-harness-kit-2-implementation/artifacts/ev_20260503_133400_787449.transcript.log
```

## Fixture/TDD Coverage Added

- `tests/unit/test_harness_kit_2.py`
  - read-only brief leaves repo state alone and avoids recommendation/confidence fields;
  - local init/work/note/materialize keeps state ignored;
  - external state creates no checkout files;
  - sync checkpoint is binary freshness-based;
  - capture records success/failure, preserves exit code, and redacts seeded secrets;
  - handoff does not overclaim missing evidence;
  - local spec can be initialized and promoted as dry-run;
  - CLI capture preserves wrapped command exit code.
- `tests/unit/test_script_contract_prototype.py`
  - canonical script prototype delegates in deterministic order;
  - script prototype fails fast on nonzero child command.

## Notes

- `mise run check` initially failed on formatting and then type issues; both were fixed before final passing validation.
- External 4-pass review and final `mise run sync-check` are pending.
