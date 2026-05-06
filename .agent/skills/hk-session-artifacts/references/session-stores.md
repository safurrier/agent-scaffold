# Session transcript stores

Use this reference when finding exact transcript paths to attach with `hk artifact attach`.

## General rule

Prefer the path produced by the harness/tool invocation itself. Candidate discovery is only a fallback and must be confirmed by repo scope, timestamp, prompt, session id, or file contents before attaching.

Default `hk artifact attach` copies the file. Use `--no-copy` only when the transcript is too large or too sensitive to copy into HK artifacts.

## Pi

Known session location behavior:

1. `--session-dir` on the `pi` command wins.
2. `PI_CODING_AGENT_SESSION_DIR` wins over settings.
3. `settings.json` `sessionDir` may configure storage.
4. Default is `~/.pi/agent/sessions/`.

Repo-scoped default directory shape observed in this environment:

```text
~/.pi/agent/sessions/--Users-alex.furrier-git_repositories-harness-toolkit--/*.jsonl
```

Best deterministic capture for a child Pi run:

```bash
SESSION_DIR="$(mktemp -d)/pi-sessions"
pi --session-dir "$SESSION_DIR" --no-tools --no-context-files -p "Reply exactly: smoke"
find "$SESSION_DIR" -name '*.jsonl' -type f
```

Then attach the exact file:

```bash
hk artifact attach --path "$PI_SESSION_JSONL" --kind pi-session-transcript --label "Pi session transcript" --redaction unknown --target .
```

## Claude Code

For headless runs, prefer writing the stream JSONL yourself:

```bash
claude -p "Reply exactly: smoke" --output-format stream-json --verbose > /tmp/claude-session.jsonl
hk artifact attach --path /tmp/claude-session.jsonl --kind claude-session-transcript --label "Claude stream JSONL" --redaction unknown --target .
```

Claude also persists sessions under project-scoped directories:

```text
~/.claude/projects/<project-key>/<session-id>.jsonl
```

The first stream JSONL row includes `session_id`; use that ID to locate the persisted file when needed. Do not rely on global latest.

## Codex

For Codex review, prefer direct JSONL capture:

```bash
codex exec review --uncommitted --json -o /tmp/codex-review-last-message.md > /tmp/codex-review-events.jsonl
hk artifact attach --path /tmp/codex-review-events.jsonl --kind codex-review-transcript --label "Codex review JSONL" --redaction external --target .
hk artifact attach --path /tmp/codex-review-last-message.md --kind codex-review-summary --label "Codex review final message" --redaction external --target .
```

Codex also persists sessions under date directories:

```text
~/.codex/sessions/YYYY/MM/DD/*.jsonl
```

Use persisted Codex sessions only when matching by run time or session id is clear.
