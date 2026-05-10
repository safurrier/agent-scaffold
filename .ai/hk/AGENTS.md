# HK generated exports

This directory stores generated Harness Kit handoff exports for meaningful
Harness Toolkit repo work.

- Source of truth: HK ledger state (`hk start`, `hk plan`, `hk decide`,
  `hk validate`, `hk review add`, `hk sync`, `hk ready`).
- Generated package: set `WORK_ID` from `hk status --json`, then run `hk export --format handoff-dir --output ".ai/hk/$WORK_ID"`.
- Default shape: `README.md` is the single human handoff/review document, `meta.json` is machine freshness/integrity data, and `artifacts/` is for explicit durable attachments only.
- Do not hand-edit generated export contents. Update the HK ledger and regenerate.
- Historical hand-authored slice artifacts remain under `.ai/plans/` for repo
  history and scaffold/generated-repo compatibility; new Harness Toolkit repo
  work should not create new `.ai/plans` slices.
