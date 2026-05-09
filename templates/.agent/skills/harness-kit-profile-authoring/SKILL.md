---
name: harness-kit-profile-authoring
description: Mine repository validation contracts and propose Harness Kit hk profiles. Use when choosing an hk profile, when no exact repo/module profile exists, when a user asks to create a custom profile, or when inspecting CI, hooks, mise, package scripts, or repo docs to draft profile checks.
allowed-tools: Read, Grep, Glob, Bash, Write
---

# Harness Kit Profile Authoring

Use this skill to decide whether an existing `hk` profile is good enough and, if
not, to propose a custom profile for user approval.

## Quickstart

1. Discover available profiles. Start with default config; only pass
   `--profiles-dir` for an ad hoc catalog that is not already declared by
   `harness.toml`:
   ```bash
   hk profile list --target <repo-or-module> --json
   hk profile list --target <repo-or-module> --profiles-dir ~/.config/harness-toolkit/profiles --json
   ```
2. Choose the closest profile by priority:
   - exact target/module profile
   - repo-specific profile
   - stack/task-runner profile
   - `generic`
3. If there is no exact repo/module profile and the repo has recurring CI or
   task-runner validation, treat built-ins as fallbacks and mine a custom
   profile proposal. See [profile-mining.md](references/profile-mining.md).
4. Draft profile TOML in the response or a temp file. Do **not** install it
   silently.
5. Ask the user to confirm, edit, or reject the profile.
6. Before writing, check whether the destination TOML already exists. Ask for
   explicit overwrite approval or use `hk profile create`, which refuses
   overwrites unless `--force` is passed.
7. Only after confirmation, write to the explicit catalog chosen by the user,
   usually:
   ```text
   ~/.config/harness-toolkit/profiles/<name>.toml
   ```
   If the user's `harness.toml` declares `profiles_dir = "profiles"` or
   `profiles_dirs = [...]`, normal `hk profile` / `hk checks` commands load those
   files without needing `--profiles-dir`.

## Profile Mining Sources

Treat sources by authority:

1. CI workflows are merge-blocking truth.
2. Pre-commit, pre-push, lefthook, and other hook configs are local commit/push truth.
3. Repo `AGENTS.md` / `CLAUDE.md` usually identifies the fastest useful agent loop.
4. Task runners (`mise`, `just`, `make`, `npm`, `uv`) expose validation surfaces.
5. Docs and recent PR notes reveal heavier, apply, deploy, or release checks.

Read [profile-mining.md](references/profile-mining.md) before drafting anything
non-trivial.

## Drafting Rules

- Keep `hk` as planning/handoff state only. Profiles describe checks; they do
  not make `hk` run validation.
- Use concrete command templates copied from the repo or clearly marked as
  proposed.
- Include at least one fast gate, one focused-test pattern when available, and a
  handoff check.
- Add heavy/CI parity checks as optional checks with notes explaining when to run
  them.
- Prefer repo-native wrappers (`mise run check`, `mise run lint`) over expanding
  them unless CI directly uses raw commands.
- For mixed-language repos, keep separate language or CI-job checks instead of
  collapsing everything into a single built-in language profile.
- Use stable profile names such as `<repo>-root` or `<repo>-<module>`.
- Do not write `~/.config/harness-toolkit/profiles/*.toml` without user approval.
- `applies_when` and `required_when` may use repo-root-relative paths or paths
  relative to the chosen `--target`; HK reports matched paths as repo-root-relative.
- Do not overwrite an existing profile unless the user explicitly approves the
  overwrite after seeing the existing path.

## Output Format

When proposing a profile, respond with:

````markdown
## Profile recommendation

Chosen existing profile: `<profile>` / none
Reason: <one sentence>

## Mined validation contract

- Fast gate: `<command>` from <source>
- Focused tests: `<command>` from <source>
- CI parity: `<command>` from <source>
- Heavy/apply checks: `<command>` from <source>

## Proposed profile

```toml
...
```

Write this profile to `~/.config/harness-toolkit/profiles/<name>.toml`?
````

## References

- [harness-kit-workflow.md](references/harness-kit-workflow.md) — baseline `hk`
  loop, profile selection, custom profile rules, and user-level `AGENTS.md`
  snippet.
- [profile-mining.md](references/profile-mining.md) — source authority, mining
  commands, and check taxonomy.
- [examples.md](references/examples.md) — generic examples for a scaffolded repo,
  a Rust mise repo, and a dotfiles repo.
