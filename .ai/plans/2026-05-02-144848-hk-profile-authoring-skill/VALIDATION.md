# Validation

## Commands

- `python3 <USER_HOME>/.pi/agent/skills/<USER_SKILL>-skill-creator/scripts/quick_validate.py templates/.agent/skills/harness-kit-profile-authoring`
  - Result: passed; skill frontmatter/body structure is valid.
- `mise run check`
  - Result: passed before review follow-up edits; 723 tests passed.
- `python3 <USER_HOME>/.pi/agent/skills/<USER_SKILL>-docs-workflow/scripts/docs_verify.py <OLD_REPO_ROOT>`
  - Result: passed.
- `python3 <USER_HOME>/.pi/agent/skills/<USER_SKILL>-ai-context-engineering-files/scripts/validate_frontmatter.py <OLD_REPO_ROOT>`
  - Result: passed.
- `python3 <USER_HOME>/.pi/agent/skills/<USER_SKILL>-ai-context-engineering-files/scripts/verify_references.py <OLD_REPO_ROOT>`
  - Result: passed.

## Evidence

- External review found four notes; all were addressed in the generated skill and bundled skill index.
- `python3 <USER_HOME>/.pi/agent/skills/<USER_SKILL>-skill-creator/scripts/quick_validate.py templates/.agent/skills/harness-kit-profile-authoring`
  - Result: passed after Codex feedback fix for custom-profile handoff templates.
- `python3 <USER_HOME>/.pi/agent/skills/<USER_SKILL>-docs-workflow/scripts/docs_verify.py <OLD_REPO_ROOT>`
  - Result: passed after Codex feedback fix.
- `mise run sync-check -- --plan-dir .ai/plans/2026-05-02-144848-hk-profile-authoring-skill`
  - Result: passed after Codex feedback fix.
- `python3 <USER_HOME>/.pi/agent/skills/<USER_SKILL>-skill-creator/scripts/quick_validate.py templates/.agent/skills/harness-kit-profile-authoring`
  - Result: passed after adding the generic workflow reference.
- `python3 <USER_HOME>/.pi/agent/skills/<USER_SKILL>-docs-workflow/scripts/docs_verify.py <OLD_REPO_ROOT>`
  - Result: passed after adding README/docs links for user-level AGENTS guidance.
- `python3 <USER_HOME>/.pi/agent/skills/<USER_SKILL>-ai-context-engineering-files/scripts/validate_frontmatter.py <OLD_REPO_ROOT>`
  - Result: passed.
- `python3 <USER_HOME>/.pi/agent/skills/<USER_SKILL>-ai-context-engineering-files/scripts/verify_references.py <OLD_REPO_ROOT>`
  - Result: passed.
- `mise run sync-check -- --plan-dir .ai/plans/2026-05-02-144848-hk-profile-authoring-skill`
  - Result: passed after adding the generic workflow reference.
