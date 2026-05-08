# Fresh-Context Review Summary

Reviewer: builtin `reviewer` subagent, fresh context
Date: 2026-05-08

## Initial review

Two blockers were found:

1. readiness messages for dangerous skips included label and mitigation but omitted the reason;
2. root `SPEC.md` still documented the old dangerous-skip command shape and did not include `hk summary`.

## Fixes

- Updated `dangerous_skip_message()` so readiness messages include label, reason, and mitigation.
- Updated root `SPEC.md` to include `hk summary`, define `status` vs `summary` vs `handoff`, and document the required `--label` / `--reason` / `--mitigation` dangerous-skip shape.
- Updated `docs/harness-kit-lifecycle-design.md` command surface to show `review|validation|sync` for dangerous skips.

## Re-review result

No blocking findings.

The reviewer verified:

- CLI/local layers require dangerous-skip label, reason, and mitigation;
- ledger validation requires those fields;
- readiness messages include label, reason, and mitigation for validation, review, and sync skips;
- `hk summary` is wired through CLI/app/local/rendering layers;
- summary and handoff render dangerous skip metadata;
- root `SPEC.md` is aligned with the new command surface;
- focused tests cover the new behavior.
