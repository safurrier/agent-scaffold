Use the HK CLI at `ROOT/bin/hk` for this workflow. Begin by exploring the CLI/status guidance enough to use it, but do not follow a pre-written command sequence.

Work in `ROOT/repo`.

Task:

1. Start HK work for improving `normalize_name`.
2. Change the implementation and tests.
3. Record a focused validation command, but do not label it `fast-gate`.
4. Run `hk status` and inspect generic validation freshness plus required profile check status.
5. Decide whether you need to record the required `fast-gate` label or can safely skip it.
6. Write `ROOT/reports/worker-report.md` with:
   - every HK command you ran;
   - what `hk status` told you about generic validation;
   - what `hk status` told you about `profile-check:fast-gate`;
   - whether the required label behavior was clear.
