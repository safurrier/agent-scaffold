# HK config diagnostics worker report

## Commands run

From `/tmp/hk-config-diagnostics-dogfood/repo` unless otherwise noted:

- `pwd && find . -maxdepth 4 -type f | sort` — initial repo inventory; RTK summarized the visible repo files.
- `/tmp/hk-config-diagnostics-dogfood/bin/hk --help` — discovered available HK commands.
- `ls -la && find . -maxdepth 5 -type f -path './.harness/*' -print -o -path './harness*' -type f -print` — attempted local config discovery; RTK could not proxy the compound `find` predicate.
- `/tmp/hk-config-diagnostics-dogfood/bin/hk config --help` — discovered config diagnostics subcommands.
- `/tmp/hk-config-diagnostics-dogfood/bin/hk profile --help && /tmp/hk-config-diagnostics-dogfood/bin/hk brief --help && /tmp/hk-config-diagnostics-dogfood/bin/hk checks --help` — discovered read-only profile/brief/checks interfaces. Did not execute profile checks.
- `RTK_DISABLED=1 find . -maxdepth 5 -type f | sort` — complete repo file inventory without RTK find limitations.
- `/tmp/hk-config-diagnostics-dogfood/bin/hk config inspect --target . --json` — inspected resolved HK config.
- `/tmp/hk-config-diagnostics-dogfood/bin/hk config validate --target . --json` — validated deterministic config/profile/system-map references.
- `/tmp/hk-config-diagnostics-dogfood/bin/hk config audit --target . --json` — confirmed the same deterministic findings as validate.
- Read `/tmp/hk-config-diagnostics-dogfood/config/harness.toml`.
- Read `/tmp/hk-config-diagnostics-dogfood/config/system-maps/repo.toml`.
- `/tmp/hk-config-diagnostics-dogfood/bin/hk profile list --json` — listed available profiles.
- `/tmp/hk-config-diagnostics-dogfood/bin/hk profile resolve --target . --json` — confirmed target resolution.
- `/tmp/hk-config-diagnostics-dogfood/bin/hk profile show demo --json` — inspected the resolved profile's check labels without executing them.
- Read `/tmp/hk-config-diagnostics-dogfood/config/profiles/demo.toml`.
- `nl -ba /tmp/hk-config-diagnostics-dogfood/config/harness.toml` — got line numbers for the bad default profile reference.
- `nl -ba /tmp/hk-config-diagnostics-dogfood/config/system-maps/repo.toml` — got line numbers for unresolved system-map check labels.
- `/tmp/hk-config-diagnostics-dogfood/bin/hk config explain --target . --changed --json` — confirmed changed-path explanation uses profile check `fast-unit` and that system-map label `unit-tests` is unresolved.

## Diagnosis

The active HK config is outside the repo at `/tmp/hk-config-diagnostics-dogfood/config/harness.toml`. `hk config inspect --target . --json` resolves the repo target correctly:

- target: `/private/tmp/hk-config-diagnostics-dogfood/repo`
- matched target name: `dogfood`
- profile: `demo`
- system map: `/private/tmp/hk-config-diagnostics-dogfood/config/system-maps/repo.toml`

`hk config validate --target . --json` and `hk config audit --target . --json` report two deterministic config problems:

1. **Error: missing default profile**
   - File: `/tmp/hk-config-diagnostics-dogfood/config/harness.toml`
   - Line: 3
   - Current value: `default_profile = "missing-default"`
   - Problem: `missing-default` is not one of the available profiles. `hk profile list --json` shows built-ins `generic`, `python`, `go`, `rust`, `rust-mise`, plus file profile `demo`.

2. **Warning: unresolved system-map check label**
   - File: `/tmp/hk-config-diagnostics-dogfood/config/system-maps/repo.toml`
   - Lines: 10 and 15
   - Current value: `validation_checks = ["unit-tests"]`
   - Problem: the resolved `demo` profile does not define a check named `unit-tests`. It defines `fast-unit` and `docs-check`. The `fast-unit` check is the unit-test check for `src/**` paths.

No profile check commands were run. The diagnosis used HK config/profile discovery and direct TOML inspection only.

## Smallest safe proposed fix

Make the existing config references point at existing labels instead of adding new profiles/checks:

1. In `/tmp/hk-config-diagnostics-dogfood/config/harness.toml`, change line 3 from:

```toml
default_profile = "missing-default"
```

to either:

```toml
default_profile = "demo"
```

or, if the default is intended only as a generic fallback for unmatched repos:

```toml
default_profile = "generic"
```

For this dogfood config, `demo` is the narrowest local choice because the only configured target also uses `profile = "demo"`.

2. In `/tmp/hk-config-diagnostics-dogfood/config/system-maps/repo.toml`, change both unresolved labels from:

```toml
validation_checks = ["unit-tests"]
```

to:

```toml
validation_checks = ["fast-unit"]
```

This preserves the system map's intent (`Core changes should stay covered by tests`) while matching the actual unit-test check label in `/tmp/hk-config-diagnostics-dogfood/config/profiles/demo.toml`.

After applying those minimal edits, re-run:

```bash
/tmp/hk-config-diagnostics-dogfood/bin/hk config validate --target . --json
```

Expected result: deterministic config validation should pass without the missing-default-profile error or unresolved-check-label warning.
