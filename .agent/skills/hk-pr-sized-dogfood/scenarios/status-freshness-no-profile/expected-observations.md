# Expected observations

## Must observe

- Worker runs `hk status` after the follow-up edit.
- Status output names stale/uncovered path(s).
- Status output offers explicit path choices: cover source-risk paths, remove accidental paths, or `hk sync --exclude` local-only paths.
- Worker either records targeted review or explains why broad review is safer.
- Worker removes accidental tool output or records an explicit sync exclusion for intentional local-only state.

## Should observe

- Worker does not require custom profile config.
- Worker does not rerun broad review purely because “review stale.”
- Worker uses evidence/review history and path-decision guidance to avoid looping.

## Failure modes to record

- Status output is too generic to choose a next action.
- Targeted review command is unclear.
- No-profile wording overclaims readiness.
- Worker misses `--path`.
- Tool-generated files such as `uv.lock`, `__pycache__/`, or agent-local state make targeted follow-up look stale after the source-risk path is covered.
