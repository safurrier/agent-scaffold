---
name: hk-pr-sized-dogfood
description: Run PR-sized Harness Kit dogfood replay trials in temporary repos to validate HK lifecycle UX with realistic tasks and observe how agents naturally discover or misuse HK.
allowed-tools: Read, Write, Edit, Bash, Subagent
---

# HK PR-Sized Dogfood

Use this skill to test Harness Kit on realistic implementation work without touching
source repos. The goal is not primarily code quality; it is to observe the
agent's actual path through HK: where it used HK, skipped it, guessed wrong, or
hit unclear readiness/sync behavior.

## Principles

- **Use temp snapshots only.** Never run replay workers in the original repo.
- **Minimize HK guidance.** Tell workers to use HK and begin by exploring the CLI;
  do not hand them the full lifecycle unless the study is specifically about a
  fixed path.
- **Prefer PR-sized directives.** Give a clear implementation directive based on
  a real merged PR or realistic slice, but do not provide the final diff.
- **Log every HK invocation.** The study needs the complete CLI path, including
  mistakes.
- **Measure workflow behavior.** Capture validation choices, readiness failures,
  sync confusion, review behavior, and non-HK commands used for iteration.

## Current HK CLI

During harness-toolkit development, use the checkout-local shim rather than a
stale globally installed `hk`:

```bash
/Users/alex.furrier/git_repositories/harness-toolkit/scripts/hk-dev --help
```

This uses `uv --project` so it preserves the caller's cwd. That means `--target .`
refers to the temp repo where the worker is standing.

If you build your own wrapper, do **not** use `uv --directory ... run hk` unless
you also force absolute `--target` paths; `uv --directory` changes cwd and can
make `--target .` point at harness-toolkit.

For the current final-polish rollout, the behavior under test is natural discoverability:

- whether workers find the lifecycle happy path without being handed it;
- whether workers use constrained sync exclusions for known local-only state;
- whether structured spec impact and fresh-context review prompts are discoverable;
- whether status phase/next-action guidance is useful without extra parent hints.

## Setup

Create a clean trial root:

```bash
ROOT=/tmp/hk-pr-sized-trials
rm -rf "$ROOT"
mkdir -p "$ROOT/bin" "$ROOT/reports"
```

Create an HK logging wrapper that delegates to the current checkout while
preserving cwd:

```bash
cat > "$ROOT/bin/hk" <<'EOF'
#!/usr/bin/env bash
set +e
LOG="${HK_DOGFOOD_LOG:-/tmp/hk-pr-sized-trials/hk-commands.jsonl}"
START_NS=$(date +%s%N)
python3 - "$LOG" "$PWD" "$START_NS" "$@" <<'PY'
import json, sys, time
log, cwd, start, *argv = sys.argv[1:]
with open(log, "a") as f:
    f.write(json.dumps({"event":"start","at":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),"cwd":cwd,"start_ns":start,"argv":argv})+"\n")
PY
/Users/alex.furrier/git_repositories/harness-toolkit/scripts/hk-dev "$@"
STATUS=$?
END_NS=$(date +%s%N)
python3 - "$LOG" "$PWD" "$START_NS" "$END_NS" "$STATUS" "$@" <<'PY'
import json, sys, time
log, cwd, start, end, status, *argv = sys.argv[1:]
with open(log, "a") as f:
    f.write(json.dumps({"event":"end","at":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),"cwd":cwd,"start_ns":start,"end_ns":end,"status":int(status),"argv":argv})+"\n")
PY
exit "$STATUS"
EOF
chmod +x "$ROOT/bin/hk"
```

## Prepare temp snapshots

For each trial repo:

1. Pick a real PR-sized change or realistic directive.
2. Identify the parent commit before the change.
3. Create a shallow, no-remote temp repo at that parent commit.
4. Create a trial branch.

Example:

```bash
mkdir -p "$ROOT/foreman"
git -C "$ROOT/foreman" init
git -C "$ROOT/foreman" fetch --depth=1 /path/to/original/repo PARENT_SHA
git -C "$ROOT/foreman" checkout -b hk-dogfood-foreman FETCH_HEAD
git -C "$ROOT/foreman" remote remove origin 2>/dev/null || true
```

This reduces forward-history cheating. Do not provide the target PR diff to the
worker.

## Worker prompt shape

Keep HK guidance intentionally small:

```text
Use the HK CLI for this workflow; begin by exploring the CLI to onboard to it.
For this trial, the HK CLI binary is /tmp/hk-pr-sized-trials/bin/hk.
Do not force a fixed command sequence; this rollout is testing natural discovery.

Task: PR_SIZED_IMPLEMENTATION_DIRECTIVE.

At the end, write /tmp/hk-pr-sized-trials/reports/NAME-worker-report.md with
what you changed, validations run, and every HK command you tried including
mistakes or places you chose not to use HK.
```

Run workers in parallel when comparing behavior across repos.

## Agent adoption snippet variant

Use this variant to test whether an agent follows only the durable user-level
AGENTS.md Harness Kit directive.

### Purpose

This is not a PR-sized implementation replay. It tests whether the short snippet
printed by `hk instructions --scope user` is enough for a fresh agent to:

- resolve the target/profile before work;
- start HK work;
- run native validation directly;
- capture validation with `hk validate --why`;
- follow `hk status` without being handed the full HK lifecycle.

### Setup

Create a small temp repo and put the generated snippet in `AGENTS.md`:

```bash
ROOT=/tmp/hk-agent-adoption-trial
rm -rf "$ROOT"
mkdir -p "$ROOT/bin" "$ROOT/repo"

cat > "$ROOT/bin/hk" <<'EOF'
#!/usr/bin/env bash
set +e
LOG="${HK_DOGFOOD_LOG:-/tmp/hk-agent-adoption-trial/hk-commands.jsonl}"
START_NS=$(date +%s%N)
python3 - "$LOG" "$PWD" "$START_NS" "$@" <<'PY'
import json, sys, time
log, cwd, start, *argv = sys.argv[1:]
with open(log, "a") as f:
    f.write(json.dumps({"event":"start","at":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),"cwd":cwd,"start_ns":start,"argv":argv})+"\n")
PY
/Users/alex.furrier/git_repositories/harness-toolkit/scripts/hk-dev "$@"
STATUS=$?
END_NS=$(date +%s%N)
python3 - "$LOG" "$PWD" "$START_NS" "$END_NS" "$STATUS" "$@" <<'PY'
import json, sys, time
log, cwd, start, end, status, *argv = sys.argv[1:]
with open(log, "a") as f:
    f.write(json.dumps({"event":"end","at":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),"cwd":cwd,"start_ns":start,"end_ns":end,"status":int(status),"argv":argv})+"\n")
PY
exit "$STATUS"
EOF
chmod +x "$ROOT/bin/hk"

cd "$ROOT/repo"
git init
git checkout -b hk-agent-adoption
/Users/alex.furrier/git_repositories/harness-toolkit/scripts/hk-dev instructions --scope user > AGENTS.md
cat > README.md <<'EOF'
# adoption trial
EOF
cat > pyproject.toml <<'EOF'
[project]
name = "adoption-trial"
version = "0.1.0"
requires-python = ">=3.12"

[tool.pytest.ini_options]
testpaths = ["tests"]
EOF
git add AGENTS.md README.md pyproject.toml
git commit --no-verify -m 'chore: init adoption trial'
```

### Worker prompt

Do not mention HK or AGENTS.md in the prompt for the realistic trial:

```text
Add a small Python utility function and tests for it. Do not commit. When done,
write /tmp/hk-agent-adoption-trial/worker-report.md summarizing what you changed
and what validation you ran.
```

If you need a controlled trial, add `Follow repo instructions.` to the prompt and
compare behavior.

### Evaluation

After the worker exits, inspect:

```bash
cat "$ROOT/hk-commands.jsonl"
git -C "$ROOT/repo" status --short
find "$ROOT/repo/.harness-local" -maxdepth 5 -type f 2>/dev/null | sort
```

Record:

- whether the agent invoked `hk profile resolve --target . --json`;
- whether it ran `hk start` before or during implementation;
- whether native validation was captured with `hk validate --why`;
- whether it followed `hk status`, `hk ready`, or `hk handoff`;
- whether it avoided committing or staging HK/local state;
- whether a missing-HK trial stops and suggests installation.

Persist the synthesis under the active `.ai/plans/.../artifacts/` directory.

## Parent collection

After workers finish, collect:

```bash
for d in TRIAL_NAMES; do
  /tmp/hk-pr-sized-trials/bin/hk ready --target "$ROOT/$d" --json || true
  /tmp/hk-pr-sized-trials/bin/hk handoff --target "$ROOT/$d" \
    --write "$ROOT/reports/$d-handoff.md" || true
  git -C "$ROOT/$d" status --short
  git -C "$ROOT/$d" diff --stat -- . ':(exclude).pi'
done
```

Parse the HK log by repo:

```bash
python3 - <<'PY'
import collections, json
log='/tmp/hk-pr-sized-trials/hk-commands.jsonl'
by=collections.defaultdict(list)
with open(log) as f:
    for line in f:
        event=json.loads(line)
        if event.get('event') != 'end':
            continue
        key='other'
        for name in ['discord-ads-ml','discord-ads-api','foreman']:
            if name in event.get('cwd', ''):
                key=name
        by[key].append(event)
for key, events in by.items():
    failures=sum(1 for event in events if event.get('status') != 0)
    commands=collections.Counter((event.get('argv') or ['no-command'])[0] for event in events)
    print(key, len(events), 'commands', failures, 'failed', commands)
PY
```

## Synthesis checklist

For each trial, record:

- baseline temp repo path and commit;
- task directive;
- changed files and untracked files;
- validation commands and whether HK captured them;
- final `hk ready` result;
- complete HK command sequence;
- HK commands that failed or were guessed incorrectly;
- places the worker chose not to use HK;
- whether context/plan/decision/review/sync/handoff were used;
- whether `hk start --plan` replaced separate start/plan commands;
- whether `hk status` changed the worker's next action;
- whether structured spec impact was used;
- whether review prompt / independent AI-tool or fresh-context review dispatch guidance was discovered (Pi `subagent`, Claude Code `Agent`/legacy `Task`, Codex Shell tool with `codex review --uncommitted` examples);
- whether readiness failures were actionable;
- whether sync freshness matched worker expectations;
- whether `hk sync --exclude` was discovered for explicit local-state risk.

## Findings to look for

Common known sharp edges:

- target confusion from wrappers or stale installed HK;
- bare command groups such as `hk evidence`;
- legacy commands attracting agents during onboarding;
- `decide` discovered only after `ready` failure;
- missing review because implementation workers cannot self-review and did not dispatch an independent AI/tool or fresh-context subagent reviewer;
- failed validation wording in handoff;
- local agent dirs such as `.pi/` affecting sync freshness;
- context under-use on PR-sized tasks.

Persist the synthesis under the active `.ai/plans/.../artifacts/` directory and
list it in `artifacts/manifest.yaml`.
