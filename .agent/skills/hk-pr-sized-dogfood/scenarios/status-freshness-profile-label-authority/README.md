# status-freshness-profile-label-authority

## Purpose

Validate that generic freshness diagnostics do not weaken profile-required check semantics. A fresh agent should see that generic validation can be fresh while a required profile label remains missing or stale.

## Product behavior under test

- Profile-required check labels remain authoritative.
- Evidence recorded under another label does not satisfy `profile-check:fast-gate`.
- `hk status` can show generic validation freshness and required label failure at the same time.

## Success signals

The worker:

- records a focused validation command that is not labeled `fast-gate`;
- runs `hk status`;
- observes generic validation freshness;
- also observes `profile-check:fast-gate` failing;
- records `fast-gate` or explicitly explains why a dangerous skip is required.

## Failure signals

The worker:

- assumes generic validation freshness satisfies `fast-gate`;
- cannot tell which required label is missing;
- reruns unrelated checks because status does not show label authority clearly.
