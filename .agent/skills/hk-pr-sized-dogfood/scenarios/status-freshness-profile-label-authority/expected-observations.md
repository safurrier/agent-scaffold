# Expected observations

## Must observe

- Worker runs `hk status` after recording validation under a non-required label or no label.
- Status shows generic validation evidence can be fresh.
- Status shows `profile-check:fast-gate` is missing or stale.
- Worker understands that a required profile label needs matching evidence or an explicit dangerous skip.

## Should observe

- Worker does not assume focused validation satisfies `fast-gate`.
- Worker records `fast-gate` if it wants readiness instead of rerunning unrelated checks.
- Worker can explain the difference between generic freshness and profile-required freshness.

## Failure modes to record

- Generic validation wording overclaims readiness.
- Required label failure is hard to find in status output.
- Worker records unrelated evidence repeatedly instead of satisfying/skipping `fast-gate`.
