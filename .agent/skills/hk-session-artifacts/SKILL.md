---
name: hk-session-artifacts
description: This skill finds and attaches Pi, Claude Code, and Codex session or review transcripts to active Harness Kit work using `hk artifact attach`. Use when the user asks to capture agent sessions, attach transcripts, preserve Codex/Claude/Pi review evidence, or inspect HK lifecycle artifacts.
---

# HK Session Artifacts

Attach real harness/tool transcript files to active Harness Kit work. Do not write a prose transcript manually. Prefer exact paths produced by the harness or command invocation.

## Workflow

1. Confirm active Harness Kit work exists:

   ```bash
   hk status --target . --json
   ```

2. Prefer an exact path from the command that produced the transcript:
   - Codex: capture `--json` stdout to a known file.
   - Claude: capture `--output-format stream-json --verbose` stdout to a known file.
   - Pi child runs: launch with explicit `--session-dir` when possible.

3. If the exact path is not known, use the candidate helper and inspect results before attaching. Treat newest-first output as an inspection aid, not an endorsement:

   ```bash
   .agent/skills/hk-session-artifacts/scripts/find_session_candidates.py --source pi --target . --limit 5
   .agent/skills/hk-session-artifacts/scripts/find_session_candidates.py --source claude --target . --limit 5
   .agent/skills/hk-session-artifacts/scripts/find_session_candidates.py --source codex --target . --limit 5
   ```

4. Attach the confirmed file with a source-specific kind:

   ```bash
   hk artifact attach --path "$TRANSCRIPT" --kind "$ARTIFACT_KIND" --label "$LABEL" --redaction unknown --target .
   ```

   Common kinds: `pi-session-transcript`, `claude-session-transcript`, `codex-review-transcript`, `codex-review-summary`, `codex-session-transcript`.

5. Render or inspect handoff:

   ```bash
   hk handoff --target .
   ```

## Safety rules

- Prefer exact producer-provided paths over latest-session heuristics.
- Never attach global latest sessions without confirming timestamp, repo scope, prompt, session id, or file contents.
- Default copy is appropriate for intentional review transcripts and small session exports.
- Use `--no-copy` only when the transcript is too large or too sensitive to copy into HK artifacts; record the reason in context/decision if handoff readers need to know.
- Use `--redaction external` when a tool or harness already produced a curated transcript; use `unknown` for raw agent sessions.

## Recipes

### Codex review transcript

```bash
OUT="$(mktemp -d)"
codex exec review --uncommitted --json -o "$OUT/codex-last.md" > "$OUT/codex-events.jsonl"
hk artifact attach --path "$OUT/codex-events.jsonl" --kind codex-review-transcript --label "Codex review JSONL" --redaction external --target .
hk artifact attach --path "$OUT/codex-last.md" --kind codex-review-summary --label "Codex review final message" --redaction external --target .
```

### Claude headless transcript

```bash
OUT="$(mktemp -d)"
claude -p "Review this change" --output-format stream-json --verbose > "$OUT/claude-stream.jsonl"
hk artifact attach --path "$OUT/claude-stream.jsonl" --kind claude-session-transcript --label "Claude stream JSONL" --redaction unknown --target .
```

### Pi child-session transcript

```bash
OUT="$(mktemp -d)"
pi --session-dir "$OUT/pi-sessions" --no-tools --no-context-files -p "Review this change"
find "$OUT/pi-sessions" -name '*.jsonl' -type f | tee "$OUT/pi-session-files.txt"
test "$(wc -l < "$OUT/pi-session-files.txt")" -eq 1
PI_SESSION="$(cat "$OUT/pi-session-files.txt")"
hk artifact attach --path "$PI_SESSION" --kind pi-session-transcript --label "Pi session transcript" --redaction unknown --target .
```

## More detail

Read `references/session-stores.md` for session store paths and source-specific notes.
