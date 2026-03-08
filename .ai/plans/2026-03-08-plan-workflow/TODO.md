---
id: plan-workflow-todo
title: Plan Workflow — Task List
description: >
  Add plan-based workflow to agent-scaffold: mise task, templates, example,
  plan-sync skill, AGENTS.md convention.
---

# TODO — plan-workflow

## Phase 1: Plan Templates
- [ ] Create `templates/.ai/plans/AGENTS.md` — routing index explaining how plans work
- [ ] Create plan file templates with frontmatter:
  - [ ] `META.yaml` template
  - [ ] `TODO.md` template
  - [ ] `LEARNING_LOG.md` template
  - [ ] `VALIDATION.md` template
  - [ ] `SPEC.md` template (optional file, still generated)
  - [ ] `IMPLEMENTATION.md` template (optional file, still generated)
- [ ] Create `templates/.ai/plans/_example/` — complete example plan agents can reference
  - [ ] Realistic META.yaml, TODO, LEARNING_LOG, VALIDATION with good entries
  - [ ] Show the progression: planned → in-progress → complete

## Phase 2: `mise run plan` Task
- [ ] Create `.mise/tasks/plan` script that:
  - [ ] Takes slug as first argument (required)
  - [ ] Creates `.ai/plans/YYYY-MM-DD-HHmm-<slug>/` directory
  - [ ] Copies plan templates into it
  - [ ] Auto-fills META.yaml: created date, current branch (if not main)
  - [ ] Prints the created path and next steps
  - [ ] If on main: warns "you're on main, create a branch first"
- [ ] Update contract tests: verify plan task exists
- [ ] Verify: `mise run plan -- test-slug` creates correct structure

## Phase 3: `/plan-sync` Skill
- [ ] Create `.agent/skills/plan-sync/SKILL.md`
  - [ ] Check META.yaml: status reflects reality, PR filled in if exists
  - [ ] Check TODO.md: completed items match actual changes
  - [ ] Check LEARNING_LOG.md: has entries if work has been done
  - [ ] Check VALIDATION.md: has entries if code has been tested
  - [ ] Report: what needs updating or "plan is current"
- [ ] Copy to `templates/.agent/skills/plan-sync/` for generated repos

## Phase 4: AGENTS.md Template Update
- [ ] Add "Starting Work" section referencing `mise run plan`
- [ ] Update "Before Pushing" section to include `/plan-sync`
- [ ] Update scaffold's own AGENTS.md to match

## Phase 5: Tests
- [ ] Add META.yaml parser + validator to `_docs_helpers.py`
- [ ] Contract tests: plan task exists and is executable
- [ ] Contract tests: plan templates exist (AGENTS.md, all file templates)
- [ ] Contract tests: example plan has all required files with valid META.yaml
- [ ] Contract tests: plan file templates have frontmatter
- [ ] Golden output test: `mise run plan -- test-slug` creates correct structure
- [ ] E2E test: generated repos include `.ai/plans/AGENTS.md`
- [ ] `mise run check` green
- [ ] Run pre-push skills including plan-sync
- [ ] Push, open PR

## Follow-on
- [ ] Review findings implementation (uses the plan workflow we just built)
