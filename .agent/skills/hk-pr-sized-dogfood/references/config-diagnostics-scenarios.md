# HK Config Diagnostics Dogfood Scenarios

Purpose: test whether fresh agents can discover and use `hk config` to diagnose broken profile/system-map configuration without being handed the exact command sequence. These are real dogfood scenarios for agent replay studies, not pytest names; scripted versions belong under the `agent_sim` marker.

## Common worker prompt

```text
This repository has broken Harness Kit configuration. Diagnose what is wrong and propose the smallest safe fix. Do not edit files unless you are certain and the prompt explicitly asks you to repair it. Use CLI help/discovery as needed. Write a report with the commands you ran, the diagnosis, and the proposed fix.
```

Evaluation questions:

- Did the worker discover `hk config --help` and the relevant subcommand help?
- Did it choose `inspect`, `validate`, or `explain` based on the problem?
- Did it distinguish advisory warnings from strict failures?
- Did it avoid running profile check commands while only diagnosing config?
- Did it avoid inventing hidden readiness policy or fake profile checks?
- Did it route judgment-heavy repairs through `hk-config-authoring`, `harness-kit-profile-authoring`, or `hk-system-map-author` when skills are available?

## Scenario 1: Missing default profile

Seed:

```toml
version = 1
profiles_dir = "profiles"
default_profile = "missing-default"
```

Expected diagnosis:

- `hk config validate --target . --json` reports `missing-default-profile`.
- The worker proposes adding the missing profile or correcting `default_profile`.
- The worker does not create a profile without confirming the intended validation contract.

## Scenario 2: Target points to a missing profile

Seed:

```toml
[[targets]]
path = "."
profile = "python-app"
```

but no `python-app` profile exists.

Expected diagnosis:

- `hk config inspect --target . --json` shows failed/missing profile resolution.
- `hk config validate --target . --json` reports the missing target profile reference.
- The worker proposes correcting the target binding or authoring the profile through the profile authoring flow.

## Scenario 3: Missing target-level system map

Seed:

```toml
[[targets]]
path = "."
profile = "root"
system_map = "system-maps/root.toml"
```

but `system-maps/root.toml` is absent.

Expected diagnosis:

- `hk config validate --target . --json` reports a missing target system-map file.
- The worker treats this as config drift, not as failed validation evidence.
- The worker proposes adding the file or correcting the path.

## Scenario 4: Stale system-map check label after profile rename

Seed:

```toml
# profile
[[checks]]
name = "fast-unit"

# system map
validation_checks = ["unit"]
```

Expected diagnosis:

- Relaxed `hk config validate --target . --json` returns `ok: true` with an `unresolved-check-label` warning.
- Strict `hk config validate --target . --strict-labels --json` returns nonzero with `ok: false`.
- The worker identifies the stale system-map label.
- The worker does **not** add a fake `unit` profile check merely to satisfy the map.
- The worker proposes updating/removing the system-map label or intentionally adding a real profile check only if the validation contract needs one.

## Scenario 5: Explain changed docs/source paths

Seed:

- Profile has `docs-check` rules for `docs/**` and `unit-tests` rules for `src/**`.
- System map has `docs` and `core` components for those paths.
- Working tree has changed files under both directories.

Expected diagnosis:

- `hk config explain --target . --changed --json` surfaces the docs/source checks and relevant system context.
- The worker can explain why each check/review/context item surfaced.
- The worker does not run the checks just to explain config applicability.

## Scenario 6: Explain a single explicit path

Seed:

- Same profile/system-map as Scenario 5.
- No Git diff is required.

Expected diagnosis:

- `hk config explain --target . --path src/app.py --json` explains only the explicit path.
- The worker uses repeated `--path` values for multiple explicit files instead of combining `--changed` and `--path`.

## Scenario 7: Skill-led repair routing

Seed:

- Profile and system map are both present but drifted: a check label is stale and a new module path has no system-map component.

Expected diagnosis:

- The worker uses `hk config validate`/`audit` to identify deterministic defects.
- The worker routes authoring/repair judgment through `hk-config-authoring`.
- The router directs stale label repair to `hk-system-map-author` and validation contract changes to `harness-kit-profile-authoring`.
- The worker reruns `hk config validate` after any repair.
