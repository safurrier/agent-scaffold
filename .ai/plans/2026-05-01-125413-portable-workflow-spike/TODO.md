---
id: plan-todo
title: Task List
description: >
  Checkable tasks for this unit of work. Check off as you go.
  See _example/ for a reference.
---

# TODO — portable-workflow-spike

- [x] Identify the existing slice-workflow CLI boundaries and repo-root assumptions
- [x] Add a portable workflow CLI path that can run against an arbitrary target repo
- [x] Add attach/plan/status/sync-check behavior for external and overlay state modes
- [x] Prove the workflow against a cloned existing repo without modifying committed files
- [x] Document findings, tradeoffs, and follow-up hardening work
- [x] Move the portable workflow command surface to Cyclopts for typed agent-facing CLI behavior
- [x] Apply agent-friendly CLI principles: non-interactive flags, JSON output, dry-run, examples, idempotent attach, actionable errors
- [x] Design and document a minimal `AGENTS.md` snippet that harnesses can use in any repo
- [x] Add a built-in profile/check DSL that describes named verification loops without executing them
- [x] Add profile/check discovery commands and profile-specific instructions
- [x] Add full tests and validation for the profile DSL dogfood slice
- [x] Remove private/company-specific profile examples from public repo files
- [x] Fully migrate public CLI surfaces from Click to Cyclopts
- [x] Remove pre-emptive `--module` workflow scoping in favor of explicit `--target` scoped paths
