# Dogfood summary — HK artifact attach

## Scenario

A temp repo was created at the path recorded in `artifacts/dogfood/tmp-root.txt`.
The dogfood verified two transcript-style artifact cases:

1. **Codex review transcript** — copied into HK work artifacts with default copy behavior.
2. **Current Pi session transcript** — recorded by source path, size, and sha256 only with `--no-copy` so private session contents were not copied into committed artifacts.

## Result

- `hk artifact attach --kind codex-review-transcript ...` succeeded and copied the Codex rereview JSONL into `.harness-local/.../artifacts/`.
- `hk artifact attach --kind pi-session-transcript --no-copy ...` succeeded and recorded metadata for the current Pi session JSONL.
- `hk validate` captured a command proving both artifact kinds exist in the lifecycle ledger.
- `hk ready` returned `ready: true`, `status: ready`.
- `hk handoff` rendered both attached artifacts under `## Attached artifacts`.

## Key artifacts

- Complete HK command log: `artifacts/dogfood/hk-commands.jsonl`
- HK lifecycle event log: `artifacts/dogfood/events.jsonl`
- HK evidence log: `artifacts/dogfood/evidence.jsonl`
- Handoff: `artifacts/dogfood/handoff.md`
- PR handoff: `artifacts/dogfood/pr-handoff.md`
- Codex initial review finding: `artifacts/dogfood/codex-review-last-message-with-initial-finding.md`
- Codex rereview result: `artifacts/dogfood/codex-rereview-last-message.md`
- Copied Codex transcript artifact: `artifacts/dogfood/artifact_20260506_115838_243386_codex-review-transcript_codex-rereview-events.jsonl`
- Pi session metadata output: `artifacts/dogfood/artifact-pi-session.json`
