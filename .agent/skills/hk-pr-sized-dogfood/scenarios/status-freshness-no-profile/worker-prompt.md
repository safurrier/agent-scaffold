Use the HK CLI at `ROOT/bin/hk` for this workflow. Begin by exploring the CLI/status guidance enough to use it, but do not follow a pre-written command sequence.

Work in `ROOT/repo`.

Task:

1. Start HK work for improving `normalize_name`.
2. Change the implementation and tests.
3. Record validation and review evidence.
4. After review, make one small follow-up source edit and create one obvious local-only/tool-output file that should not be reviewed.
5. Use `hk status` to decide whether to rerun broad review, record targeted follow-up, remove accidental files, or explicitly exclude local-only files.
6. Prefer the narrowest safe follow-up if status gives enough information; for intentional local-only state, prefer an auditable `hk sync --exclude ... --reason ...` over broad review.
7. Write `ROOT/reports/worker-report.md` with:
   - every HK command you ran;
   - what `hk status` told you;
   - whether you reran broad review or used targeted follow-up;
   - whether you removed or excluded the local-only/tool-output file;
   - what was confusing.
