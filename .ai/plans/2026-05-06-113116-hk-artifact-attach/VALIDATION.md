---
id: plan-validation
title: Validation Evidence
description: >
  Commands run and what they proved.
---

# VALIDATION — hk-artifact-attach

## Focused checks

```bash
uv run ruff check src/harness_toolkit/kit/local.py src/harness_toolkit/kit/app/lifecycle.py src/harness_toolkit/kit/cli.py src/harness_toolkit/kit/ledger/store.py src/harness_toolkit/kit/rendering/handoff.py tests/unit/test_harness_kit_2.py README.md SPEC.md docs/portable-workflow.md docs/harness-kit-2-design.md AGENTS.md
```

Result: passed.

```bash
uv run ty check src/harness_toolkit/kit/local.py src/harness_toolkit/kit/app/lifecycle.py src/harness_toolkit/kit/cli.py src/harness_toolkit/kit/ledger/store.py src/harness_toolkit/kit/rendering/handoff.py tests/unit/test_harness_kit_2.py
```

Result: passed.

```bash
uv run pytest tests/unit/test_harness_kit_2.py -q
```

Result before e2e help-test fix: `72 passed`.

```bash
uv run pytest tests/unit/test_harness_kit_2.py tests/e2e/test_hk2_cli_parity.py tests/e2e/test_harness_kit_rollout.py -q
```

Result after addressing Codex finding: `78 passed`.

## Full gate

```bash
mise run check
```

Result: passed; `822 passed`.

## Codex review

```bash
codex exec review --uncommitted --json -o /tmp/hk-artifact-dogfood.K0vW7c/codex-review-last-message.md > /tmp/hk-artifact-dogfood.K0vW7c/codex-review-events.jsonl 2>&1
```

Initial result: one blocker about e2e legacy help checks still rejecting any `attach` text.

```bash
codex exec review --uncommitted --json -o /tmp/hk-artifact-dogfood.K0vW7c/codex-rereview-last-message.md > /tmp/hk-artifact-dogfood.K0vW7c/codex-rereview-events.jsonl 2>&1
```

Rereview result: no blocking issues.

## HK artifact dogfood

Dogfood artifacts are under `artifacts/dogfood/`.

Key command sequence:

```bash
hk start artifact-attach --plan 'Verify hk artifact attach can attach a copied Codex review transcript and a referenced Pi session transcript.'
hk artifact attach --path /tmp/hk-artifact-dogfood.K0vW7c/codex-rereview-events.jsonl --kind codex-review-transcript --label 'Codex rereview JSONL transcript copied into HK artifacts' --redaction external
hk artifact attach --path ~/.pi/agent/sessions/.../session.jsonl --kind pi-session-transcript --label 'Current Pi session JSONL referenced by path/hash only; not copied' --redaction unknown --no-copy
hk validate --why 'Verify attached artifact metadata is present in the HK lifecycle event ledger.' -- python3 -c '...'
hk ready
hk handoff --write /tmp/.../handoff.md
```

Result:

- `artifacts/dogfood/ready.json`: `ready: true`, `status: ready`.
- `artifacts/dogfood/handoff.md`: renders both attached artifacts.
- Codex review transcript is copied into HK artifacts.
- Pi session transcript is reference-only with source path, size, and sha256; private transcript contents were not copied into the plan artifact directory.
- `artifacts/dogfood/events.jsonl`: includes two `artifact_attached` events.
- `artifacts/dogfood/evidence.jsonl`: captures the validation command proving the ledger contains both artifact kinds.
