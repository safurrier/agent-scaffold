# Validation

## Commands

```bash
uv run pytest -m contract
```

Result: passed — 255 tests.

```bash
uv run pytest tests/unit/test_harness_kit_2.py -q
```

Result: passed — 14 tests after final review fixes.

```bash
uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_script_contract_prototype.py -q
```

Result: passed — 10 tests before final review-fix tests were added.

```bash
uv run pytest -m "not slow"
```

Result: passed — 599 tests before script-prototype tests were added.

```bash
mise run check
```

Result: passed — format, lint, typecheck, and full non-slow test gate. Initial captured evidence recorded in local Harness Kit 2 ledger:

```text
.harness-local/harness-kit/root/work/2026-05-03-132345-harness-kit-2-implementation/artifacts/ev_20260503_133400_787449.transcript.log
```

```bash
mise run check
```

Result: passed after addressing first Codex review findings. Captured evidence recorded in local Harness Kit 2 ledger:

```text
.harness-local/harness-kit/root/work/2026-05-03-132345-harness-kit-2-implementation/artifacts/ev_20260503_135034_228031.transcript.log
```

```bash
mise run check
```

Result: passed after addressing follow-up Codex review findings. Captured evidence recorded in local Harness Kit 2 ledger:

```text
.harness-local/harness-kit/root/work/2026-05-03-132345-harness-kit-2-implementation/artifacts/ev_20260503_140555_376622.transcript.log
```

```bash
mise run check
```

Result: passed after addressing final Codex review findings. Final captured evidence recorded in local Harness Kit 2 ledger:

```text
.harness-local/harness-kit/root/work/2026-05-03-132345-harness-kit-2-implementation/artifacts/ev_20260503_142235_218001.transcript.log
```

```bash
mise run sync-check -- --plan-dir .ai/plans/2026-05-03-131749-harness-kit-2-ledger-assistant
```

Result: passed — plan, spec/decision, evidence, and review contracts ready.

## Fixture/TDD Coverage Added

- `tests/unit/test_harness_kit_2.py`
  - read-only brief leaves repo state alone and avoids recommendation/confidence fields;
  - local init/work/note/materialize keeps state ignored;
  - external state creates no checkout files and uses isolated `XDG_STATE_HOME`;
  - sync checkpoint is binary/freshness-based and tracks staged, untracked, and untracked-content changes;
  - capture records success/failure/missing-executable evidence, preserves exit code, and redacts seeded key/value and split-argument secrets;
  - capture JSON stdout remains parseable;
  - invalid handoff formats are rejected;
  - handoff does not overclaim missing evidence;
  - local spec can be initialized and promoted as dry-run;
  - CLI capture preserves wrapped command exit code.
- `tests/unit/test_script_contract_prototype.py`
  - canonical script prototype delegates in deterministic order;
  - script prototype fails fast on nonzero child command.

## Notes

- `mise run check` initially failed on formatting and then type issues; both were fixed before final passing validation.
- External 4-pass review completed and findings were addressed.
- Final `mise run sync-check` recorded below after plan-contract fixes.
