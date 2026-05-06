# Dogfood summary — sync exclude literal paths

## Scenario

A temp repo was created at the path recorded in `artifacts/dogfood/tmp-root.txt`.
The dogfood made one tracked README edit and three untracked local-only paths not
under `.pi` or `.claude`:

- `dist/agent-output.json`
- `.cache/tool/session.json`
- `src/scratch.py`

The dogfood then ran HK lifecycle commands through a logging wrapper and recorded
a sync checkpoint excluding those three literal paths.

## Result

- `hk sync --exclude dist --exclude .cache/tool --exclude src/scratch.py ...` succeeded.
- `hk sync --check` returned `synced: true`.
- `hk ready` returned `ready: true`, `status: ready`.
- `hk handoff` rendered `## Sync exclusions` with the three excluded paths and reason.

## Key artifacts

- Complete HK command log: `artifacts/dogfood/hk-commands.jsonl`
- HK lifecycle event log: `artifacts/dogfood/events.jsonl`
- HK evidence log: `artifacts/dogfood/evidence.jsonl`
- Captured validation transcript: `artifacts/dogfood/ev_20260506_101108_788162.transcript.log`
- Handoff: `artifacts/dogfood/handoff.md`
- PR handoff: `artifacts/dogfood/pr-handoff.md`
- Readiness JSON: `artifacts/dogfood/ready.json`
- Sync check JSON: `artifacts/dogfood/sync-check.json`
