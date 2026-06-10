---
id: harness-toolkit-adr-0013
title: ADR 0013 — Web Stack V0
description: >
  Accepts the first supported Web stack for harness-scaffold: Vite/React browser
  app, Cloudflare Worker API, D1 migration scaffold, and npm-backed validation.
index:
  - id: decision
    keywords: [web-stack, vite, react, cloudflare, workers, d1]
  - id: consequences
    keywords: [vercel, postgres, r2, auth, follow-up]
---

# ADR 0013: Web Stack V0

**Status**: Accepted  
**Date**: 2026-06-08  
**Deciders**: Alex Furrier  
**Generated from**: hk work item `2026-06-07-174855-web-stack-v0`

---

## Context

Harness Scaffold already supported Python, Go, and Rust stacks behind the stable
`mise run` task contract. The next target class is small app-shaped web projects
with likely needs for deploy previews, a custom domain, login, and saved runs.

The planning trade-off was whether to start with Vercel plus common external
services, or a Cloudflare-native baseline. Cloudflare is a good first target
because one platform can host static assets, execute API routes, and provide D1
relational persistence. The template still needs to stay boring and reversible:
no fake adapters for platforms that are not wired yet, and no over-abstracted
persistence layer in the default path. However, the first real app workflows
commonly want Tailwind, shadcn/ui conventions, and Drizzle over D1, so those are
supported as opt-in web variants rather than defaults.

## Decision

Add `web` as a supported `harness-scaffold` stack.

The generated V0 uses:

- Vite + React for the browser app;
- Cloudflare Workers + Static Assets for hosting and API routes;
- D1 migrations for relational saved-run state, with optional Drizzle-over-D1
  query code;
- npm scripts behind the standard `setup`, `fmt`, `lint`, `typecheck`, `test`,
  `build`, `check`, `dev`, and `verify` tasks;
- Prettier, ESLint, TypeScript, and Vitest as the fast validation gate;
- optional Tailwind and shadcn/ui generated UI scaffolding.

The default remains plain CSS plus raw D1 prepared statements. The opt-in
variants are `--web-ui tailwind`, `--web-ui shadcn`, and `--web-db drizzle-d1`.
The template includes saved-run API routes and an auth placeholder document, but
does not choose an auth provider. Vercel, Postgres, R2, and richer auth support
remain follow-up stack variants or optional modules, not inert V0 adapters.

## Consequences

### Positive

- New web apps get the same task contract as existing stacks.
- The generated repo can deploy to Cloudflare with static assets and Worker
  routes from day one.
- D1 gives generated web apps a relational persistence path for login-owned
  saved runs without introducing external Postgres setup in the template.
- Agents can opt into the app starter Alex usually wants (`--web-ui shadcn
  --web-db drizzle-d1`) without making every generated web repo inherit those
  opinions.
- PR/merge deploy preview workflows can build on Cloudflare or a future Vercel
  platform module without changing the core app structure.

### Negative / Trade-offs

- The first supported web stack is Cloudflare-oriented, not platform-neutral.
- D1 is SQLite-compatible and Cloudflare-hosted; teams that specifically need
  Postgres will add a separate persistence module later.
- Auth and custom domains remain explicit post-init setup steps.
- npm install introduces network-bound setup into the generated web smoke tests.
- The optional UI/DB variants increase the validation matrix for web-stack
  changes.

## Follow-ups

- Add a how-to for custom domains once the first real generated web app is
  deployed.
- Add an auth module after the first generated apps settle on a provider shape.
- Consider Vercel and Postgres as explicit stack options only after a real app
  needs them.
- Add R2 support when a generated app needs object/blob storage.
