# Review Summary — hk-profiles-module-split

Fresh-context `reviewer` subagent reviewed the profile module split.

## Initial findings

Blocking findings:

- `harness_toolkit.kit.profiles` no longer re-exported `BUILTIN_PROFILES` or `loaded_builtins`, which were importable from the package root before the refactor.
- `profiles_to_json({})` changed behavior. The previous implementation treated an empty dict as falsy and fell back to the default loaded catalog; the split implementation returned zero profiles.

Non-blocking finding:

- `config.py` imports parser helper `_required_str`; acceptable for now, but could be promoted if the helper grows.

## Fixes

- Restored root re-exports for `BUILTIN_PROFILES` and `loaded_builtins`.
- Restored the prior falsy-empty-catalog fallback in `profiles_to_json`.
- Added package-boundary tests for root exports and `profiles_to_json({})` fallback.

## Re-review disposition

Accepted. Re-review found no blockers and confirmed import compatibility, fallback behavior, and circular import risk are addressed.
