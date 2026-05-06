# Harness Kit Workflow Reference

Use this reference when a session is not already familiar with Harness Kit (`hk`)
or when adding `hk` guidance to a user-level `AGENTS.md`.

## Baseline Loop

Use Harness Kit for meaningful code changes unless stronger repo-specific
instructions supersede it.

Start by printing current agent instructions:

```bash
hk instructions --profile generic --json
```

Then choose target and profile:

```bash
hk profile list --target <repo-or-module> --profiles-dir ~/.config/harness-toolkit/profiles --json
hk start <slug> --plan 'Adopted implementation intent' --target <repo-or-module> --json
hk status --target <repo-or-module> --json
hk checks --target <repo-or-module> --profile <profile> --profiles-dir ~/.config/harness-toolkit/profiles --json
hk sync --target <repo-or-module> --json
hk ready --target <repo-or-module> --json
```

Omit `--profiles-dir` only when intentionally using built-in profiles only.

## Rules

- `hk` manages planning and handoff state. It does **not** run validation commands.
- Run profile-suggested validation commands directly in the shell.
- Record exact command/result evidence with `hk validate --why`.
- Use the same `--target`, `--profile`, and `--profiles-dir` consistently for
  profile/check commands. Lifecycle status/ready state is target-scoped.
- Do not commit `.ai/`, `.agent/`, `.mise/`, or `.gitignore` workflow files
  unless explicitly asked. HK2 local state lives under `.harness-local/`.
- For repos that already have committed scaffold/task-contract infrastructure
  and repo-local plans are expected, native committed workflow is okay.

## Profile Selection

1. Run:
   ```bash
   hk profile list --target <repo-or-module> --profiles-dir ~/.config/harness-toolkit/profiles --json
   ```
2. Choose the closest profile:
   - exact target/module profile
   - repo-specific profile
   - stack/task-runner profile
   - `generic`
3. Tell the user once which profile was chosen and why.

Built-in language profiles are fallbacks, not authoritative contracts, when a
repo has recurring CI or task-runner validation.

## Custom Profiles

If no exact module/repo profile exists and the repo has a recurring validation
contract, ask the user whether to create one. Do not silently create profiles.

```bash
hk profile create <repo-or-module-name> \
  --target <repo-or-module-path> \
  --preset <generic|python|go|rust|rust-mise> \
  --profiles-dir ~/.config/harness-toolkit/profiles
```

After creating a profile template, have the user confirm or edit TODOs and
command templates before treating it as authoritative.

If a good profile does not exist, use this skill to mine CI workflows, hooks,
task runners, repo docs, and recent validation evidence before proposing TOML.

## User-Level AGENTS.md Snippet

Append a compact version like this to a user-level `AGENTS.md` when the user
wants agents to default to Harness Kit across arbitrary repos:

````markdown
## Harness Kit Workflow

For meaningful code changes, use Harness Kit (`hk`) as the default planning and
handoff loop unless stronger repo-specific instructions supersede it.

If the current session is not already familiar with the `hk` workflow, it MUST:

1. Print the current instructions:
   ```bash
   hk instructions --profile generic --json
   ```
2. Read the local Harness Kit workflow reference if one is available.

If already familiar with the workflow, do not reload the full reference just for
ceremony. Still use the managed profile catalog when selecting profiles:

```bash
hk profile list --target <repo-or-module> --profiles-dir ~/.config/harness-toolkit/profiles --json
```

Rules to remember:

- `hk` manages planning/handoff state; it does not run validation commands.
- Run validation directly and record exact command/result evidence with `hk validate --why`.
- Keep `--target`, `--profile`, and `--profiles-dir` consistent across `hk` commands.
- If no good profile exists, use the profile-authoring workflow to propose one;
  do not create profiles silently.
````
