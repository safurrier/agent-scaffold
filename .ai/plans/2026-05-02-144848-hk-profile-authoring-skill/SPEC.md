---
id: plan-spec
title: Harness Kit Profile Authoring Skill Specification
description: >
  Requirements for shipping a profile-authoring skill with harness-scaffold
  generated repos.
---

# Specification — hk-profile-authoring-skill

## Problem

Harness Kit supports custom profile catalogs, but agents need reusable guidance
for deciding when built-in profiles are only fallbacks and for mining repo CI,
hooks, task runners, and docs before proposing a custom profile.

## Requirements

### MUST

- Add a reusable skill that explains how to mine validation contracts and draft
  `hk` custom profiles.
- Keep profile creation user-approved; do not instruct agents to silently write
  profile TOML.
- Cover CI, hooks, AGENTS/CLAUDE docs, task runners, and recent validation
  evidence as profile-mining sources.
- Include generic examples without relying on private/company-specific context.

### SHOULD

- Mention the skill from portable workflow docs.
- Preserve `hk`'s model: profile checks describe commands; agents run validation
  directly in the shell loop.

## Constraints

- Do not add a new `hk` command for profile mining.
- Do not add hidden implicit profile config discovery.
