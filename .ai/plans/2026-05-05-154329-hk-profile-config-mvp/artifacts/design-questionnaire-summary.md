# HK profile/config MVP questionnaire summary

Date: 2026-05-05

## Decisions

- Implement user config + inline profiles only for this slice.
- Default config lookup:
  1. `$HARNESS_KIT_CONFIG`
  2. `$XDG_CONFIG_HOME/harness-toolkit/harness.toml`
  3. `~/.config/harness-toolkit/harness.toml`
- Schema starts as one file with:
  - top-level defaults;
  - `[[targets]]` explicit path bindings;
  - `[profiles.<name>]` inline profile definitions;
  - `[[profiles.<name>.checks]]` check definitions.
- Resolve profiles with explicit longest path prefix matching.
- `hk checks --target .` should use the resolved profile when `--profile` is omitted and config explicitly resolves one.
- Repo-level `.harness/harness.toml` is documented/deferred only.
- Review backend config is instructions/examples only for now; no structured backend schema yet.
- Include harness-toolkit, foreman, and dread sample profiles in docs/dogfood config.
- Dogfood after implementation in temp clones of dread and foreman.

## Rationale

This keeps HK shell-first and avoids heuristic auto-selection while solving the practical user problem: agents can work across known repos/modules without the human re-explaining validation commands every session.
