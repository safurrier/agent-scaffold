# Sync exclude literal-path dogfood

Temp repo: /tmp/hk-sync-exclude-dogfood.KrcMCh/repo
HK command log: artifacts/dogfood/hk-commands.jsonl
Evidence log: artifacts/dogfood/evidence.jsonl
Handoff: artifacts/dogfood/handoff.md
PR handoff: artifacts/dogfood/pr-handoff.md

Scenario:
- made one tracked README edit that must remain in the sync fingerprint;
- created untracked local-only paths outside .pi/.claude: dist/, .cache/tool/, src/scratch.py;
- ran hk sync with all three literal paths excluded;
- verified hk sync --check and hk ready passed;
- rendered handoff artifacts showing the recorded exclusions.
