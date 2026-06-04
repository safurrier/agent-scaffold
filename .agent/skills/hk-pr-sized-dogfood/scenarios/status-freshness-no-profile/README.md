# status-freshness-no-profile

## Purpose

Validate that `hk status` is useful in a repository with no custom `harness.toml` or profile binding. A fresh agent should understand generic stale path freshness and choose a targeted review follow-up instead of rerunning broad review just because status reports stale review evidence.

## Product behavior under test

- Generic evidence freshness works without profile config.
- `hk status` names stale/uncovered paths.
- `hk status` suggests targeted follow-up when a previously reviewed path changes.
- Generic wording does not claim repo-specific required validation passed.

## Success signals

The worker:

- starts HK work;
- records validation and external-enough review evidence;
- makes a small source follow-up after review;
- runs `hk status` after the follow-up edit;
- records a targeted review for the stale path, or explains why broad review is safer;
- does not require custom profile config to find useful status guidance.

## Failure signals

The worker:

- reruns broad review only because status wording is unclear;
- thinks no-profile means HK cannot help;
- misses the targeted `--path` follow-up affordance;
- treats generic validation freshness as a named repo-specific required check.
