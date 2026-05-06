# Artifact attach dogfood

Temp repo: /tmp/hk-artifact-dogfood.K0vW7c/repo
Pi session referenced with --no-copy: /Users/alex.furrier/.pi/agent/sessions/--Users-alex.furrier-git_repositories-harness-toolkit--/2026-05-03T19-41-06-705Z_019def5b-d711-710e-9285-06c785a17f7a.jsonl
Codex rereview transcript copied from: /tmp/hk-artifact-dogfood.K0vW7c/codex-rereview-events.jsonl

Scenario:
- attach a Codex review JSONL transcript with default copy behavior;
- attach the current Pi session JSONL with --no-copy so private session contents are not copied into HK artifacts;
- validate that both artifact kinds are present in the HK lifecycle event ledger;
- render handoff and PR handoff showing attached artifact metadata.
