# Harness Kit Workflow Reference

Use this reference when a session is not already familiar with Harness Kit (`hk`)
or when adding `hk` guidance to a user-level `AGENTS.md`.

## Baseline Loop

Use Harness Kit for meaningful code changes unless stronger repo-specific
instructions supersede it.

Start by printing current agent instructions:

```bash
hk instructions --scope user --json
```

Then choose target and profile:

```bash
hk profile list --target <repo-or-module> --json
hk start <slug> --plan 'Adopted implementation intent' --target <repo-or-module> --json
hk status --target <repo-or-module> --json
hk checks --target <repo-or-module> --profile <profile> --json
hk sync --target <repo-or-module> --json
hk ready --target <repo-or-module> --json
```

Only pass `--profiles-dir` for an ad hoc catalog not already declared by user
config. User-level `harness.toml` can declare `profiles_dir = "profiles"` or
`profiles_dirs = [...]` so standalone profile files load by default.

## Rules

- `hk` manages planning and handoff state. It does **not** run validation commands.
- Run profile-suggested validation commands directly in the shell.
- Record exact command/result evidence with `hk validate --why`; use
  `hk validate --check NAME --why` when satisfying a named profile check.
- Use the same `--target` and `--profile` consistently for profile/check
  discovery commands. Use `--profiles-dir` only for ad hoc catalogs. Lifecycle
  status/ready state is target-scoped and does not accept profile flags.
- Path rules in `applies_when` / `required_when` can be repo-root-relative or
  relative to the selected `--target`; HK reports matched paths as repo-root-relative.
- Do not commit `.ai/`, `.agent/`, `.mise/`, or `.gitignore` workflow files
  unless explicitly asked. Harness Kit local state lives under `.harness-local/`.
- For repos that already have committed scaffold/task-contract infrastructure
  and repo-local plans are expected, native committed workflow is okay.

## Profile Selection

1. Run:
   ```bash
   hk profile list --target <repo-or-module> --json
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
   hk instructions --scope user --json
   ```
2. Read the local Harness Kit workflow reference if one is available.

If already familiar with the workflow, do not reload the full reference just for
ceremony. Still use the managed profile catalog when selecting profiles:

```bash
hk profile list --target <repo-or-module> --json
```

Rules to remember:

- `hk` manages planning/handoff state; it does not run validation commands.
- Run validation directly and record exact command/result evidence with `hk validate --why`.
- Use `hk checks --changed` to see path-based check/review suggestions when profiles define them.
- Keep profile flags on discovery commands (`hk profile`, `hk checks`, repo-scope `hk instructions`); lifecycle commands do not accept `--profile` or `--profiles-dir`.
- Path rules in `applies_when` / `required_when` can be repo-root-relative or relative to the selected `--target`.
- If no good profile exists, use the profile-authoring workflow to propose one;
  do not create profiles silently.
````
