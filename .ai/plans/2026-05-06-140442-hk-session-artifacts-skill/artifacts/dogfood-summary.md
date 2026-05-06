# Dogfood summary — hk-session-artifacts skill

## Scenario

Created a repo-local skill that teaches agents to find and attach Pi, Claude Code, and Codex transcript files with `hk artifact attach`, preferring exact paths over latest-session guessing.

Dogfood produced exact transcript files for all three sources:

- Pi: `pi --session-dir ... --provider anthropic --model haiku --no-tools --no-context-files -p ...`
- Codex: `codex exec --json -o ... > codex-events.jsonl`
- Claude: `claude --bare -p ... --output-format stream-json --verbose --model haiku --tools '' > claude-stream.jsonl`

Then a temp HK lifecycle attached all three transcript files by exact path.

## Result

- Skill validation passed.
- Candidate helper emitted safe JSON and warnings for Pi, Claude, and Codex.
- HK dogfood reached `ready: true`, `status: ready`.
- HK handoff rendered all three attached transcript artifacts.
- No latest-session attachment automation was used.

## Key artifacts

- Skill: `.agent/skills/hk-session-artifacts/SKILL.md`
- Candidate helper: `.agent/skills/hk-session-artifacts/scripts/find_session_candidates.py`
- Session store reference: `.agent/skills/hk-session-artifacts/references/session-stores.md`
- Handoff: `artifacts/dogfood/handoff.md`
- Event ledger: `artifacts/dogfood/events.jsonl`
- Evidence ledger: `artifacts/dogfood/evidence.jsonl`
- Attached Pi transcript copy: `artifacts/dogfood/artifact_20260506_140716_491299_pi-session-transcript_pi-session.jsonl`
- Attached Codex transcript copy: `artifacts/dogfood/artifact_20260506_140718_435090_codex-session-transcript_codex-events.jsonl`
- Attached Claude transcript copy: `artifacts/dogfood/artifact_20260506_140721_040286_claude-session-transcript_claude-stream.jsonl`
