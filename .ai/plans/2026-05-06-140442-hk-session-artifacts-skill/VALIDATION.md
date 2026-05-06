---
id: plan-validation
title: Validation Evidence
description: >
  Commands run and what they proved.
---

# VALIDATION — hk-session-artifacts-skill

## Skill validation

```bash
uv run ruff check .agent/skills/hk-session-artifacts/scripts/find_session_candidates.py
```

Result: passed.

```bash
python3 /Users/alex.furrier/.pi/agent/skills/alex-ai-skill-creator/scripts/quick_validate.py .agent/skills/hk-session-artifacts
```

Result: passed; `Skill is valid!`.

```bash
python3 -m py_compile .agent/skills/hk-session-artifacts/scripts/find_session_candidates.py
```

Result: passed.

## Candidate helper smoke checks

```bash
.agent/skills/hk-session-artifacts/scripts/find_session_candidates.py --source pi --target . --limit 0
.agent/skills/hk-session-artifacts/scripts/find_session_candidates.py --source claude --target . --limit 0
.agent/skills/hk-session-artifacts/scripts/find_session_candidates.py --source codex --target . --limit 0
```

Result: all emitted valid JSON with zero candidates and heuristic warnings. Saved as:

- `artifacts/dogfood/pi-limit0-candidates.json`
- `artifacts/dogfood/claude-limit0-candidates.json`
- `artifacts/dogfood/codex-limit0-candidates.json`

## Candidate helper real checks

```bash
.agent/skills/hk-session-artifacts/scripts/find_session_candidates.py --source pi --target . --limit 5
.agent/skills/hk-session-artifacts/scripts/find_session_candidates.py --source claude --target . --limit 5
.agent/skills/hk-session-artifacts/scripts/find_session_candidates.py --source codex --target . --limit 5
```

Result: emitted repo-scoped Pi and Claude candidates plus low-confidence Codex persisted candidates with warnings. Saved under `artifacts/dogfood/*-candidates.json`.

## Headless transcript production

```bash
pi --session-dir /tmp/hk-session-skill-smoke.2HvMJi/pi-sessions --provider anthropic --model haiku --no-tools --no-context-files -p 'Reply exactly: HK_PI_SESSION_ARTIFACT_SMOKE'
```

Result: created a 2.4 KB Pi session JSONL under the explicit session dir.

```bash
codex exec --json -o /tmp/hk-session-skill-smoke-codex.BMohij/codex-last.md 'Reply exactly: HK_CODEX_SESSION_ARTIFACT_SMOKE' > /tmp/hk-session-skill-smoke-codex.BMohij/codex-events.jsonl
```

Result: created Codex JSONL event stream and final message file.

```bash
claude --bare -p 'Reply exactly: HK_CLAUDE_SESSION_ARTIFACT_SMOKE' --output-format stream-json --verbose --model haiku --tools '' > /tmp/hk-session-skill-smoke-claude.6Vo6Iq/claude-stream.jsonl
```

Result: created Claude stream JSONL.

## HK dogfood

Dogfood artifacts are under `artifacts/dogfood/`.

Key command sequence:

```bash
hk start session-artifacts --plan 'Dogfood hk-session-artifacts skill by attaching exact Pi, Codex, and Claude transcript paths.'
hk artifact attach --path /tmp/hk-session-artifacts-dogfood/pi-session.jsonl --kind pi-session-transcript --label 'Pi child session JSONL from explicit --session-dir'
hk artifact attach --path /tmp/hk-session-artifacts-dogfood/codex-events.jsonl --kind codex-session-transcript --label 'Codex exec JSONL captured to known path'
hk artifact attach --path /tmp/hk-session-artifacts-dogfood/claude-stream.jsonl --kind claude-session-transcript --label 'Claude stream JSONL captured to known path'
hk validate --why 'Verify HK ledger includes attached Pi, Codex, and Claude transcript artifact kinds.' -- python3 -c '...'
hk ready
hk handoff --write /tmp/.../handoff.md
```

Result:

- `artifacts/dogfood/ready.json`: `ready: true`, `status: ready`.
- `artifacts/dogfood/handoff.md`: renders all three attached transcript artifacts.
- `artifacts/dogfood/events.jsonl`: includes `artifact_attached` events for Pi, Codex, and Claude.
- `artifacts/dogfood/evidence.jsonl`: records the validation command proving all three artifact kinds are in the HK ledger.
