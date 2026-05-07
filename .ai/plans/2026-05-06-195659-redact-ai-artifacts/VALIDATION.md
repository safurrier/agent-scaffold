---
id: plan-validation
title: Validation Evidence
description: >
  Commands run and what they proved.
---

# VALIDATION — redact-ai-artifacts

## Commands

```bash
rg -n --hidden "/Users/(alex|alex\\.furrier)|/private/var/folders|/var/folders" .ai
```

Result: no remaining matches.

```bash
rg -n --hidden -i "\\bdiscord\\b|alex\\.furrier|alex-furrier|Alex Furrier|\\bAlex\\b|safurrier|alex-ai" .ai
```

Result: no remaining matches.

```bash
rg -n --hidden -i "obsidian-vault|datadog|notion|gmail" .ai
```

Result: no remaining matches.

```bash
rg -n --hidden -i 'ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|thinkingSignature|Authorization: Bearer [A-Za-z0-9._-]+|password":"secret' .ai
```

Result: no remaining matches.

```bash
mise run sync-check -- --plan-dir .ai/plans/2026-05-06-195659-redact-ai-artifacts
mise run sync-check -- --changed-plans main...HEAD
```

Result: passed.

## Evidence

- `artifacts/redaction-audit.log`
- `artifacts/review-summary.md`
