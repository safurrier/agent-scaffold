---
id: web-template-summary
title: Web App Template Summary
description: >
  Summary of the Harness Toolkit web stack template: what it generates, what
  validation it wires in, what Cloudflare pieces are ready, and what remains
  app-specific.
index:
  - id: generated-template
    keywords: [web, scaffold, template, react, vite, cloudflare, worker]
  - id: validation
    keywords: [validation, tests, lint, typecheck, verify, ci]
  - id: cloudflare
    keywords: [cloudflare, workers, assets, d1, r2, auth, custom-domain]
  - id: followups
    keywords: [followups, stubs, vercel, postgres, r2]
---

# Web App Template Summary

## What the web stack adds

The Harness Toolkit `web` stack creates a deployable TypeScript web app
foundation for projects that need a browser UI, API routes, and a path to
login-owned persistence.

Generate it with:

```bash
mise run init -- --non-interactive --name my-dashboard --shape single --stack web
```

The generated app uses:

- Vite + React for the browser app
- TypeScript for app, worker, and tests
- Cloudflare Workers for API routes and hosting
- Cloudflare Static Assets for serving the Vite build
- D1 migrations for relational saved-run style data
- Vitest for tests
- ESLint and Prettier for code quality
- Wrangler for local Worker development and deploy dry-runs

Optional variants:

- `--web-ui tailwind` adds Tailwind v4 through the Vite plugin
- `--web-ui shadcn` adds Tailwind plus shadcn-compatible `Button`, `cn()`, and
  `components.json` scaffolding
- `--web-db drizzle-d1` keeps Cloudflare D1 but uses Drizzle's D1 adapter and a
  generated `worker/db/schema.ts`

## Generated layout

```text
my-dashboard/
├── index.html
├── package.json
├── wrangler.jsonc
├── src/
│   ├── app/App.tsx
│   ├── main.tsx
│   ├── sim/savedRun.ts
│   └── styles.css
├── worker/
│   ├── index.ts
│   ├── auth/README.md
│   ├── db/savedRuns.ts
│   └── routes/
│       ├── health.ts
│       └── runs.ts
├── migrations/
│   └── 0001_auth_and_saved_runs.sql
├── tests/
│   ├── app.test.ts
│   └── worker.test.ts
└── public/data/.gitkeep
```

Variant-only files:

```text
components.json                  # --web-ui shadcn
src/components/ui/button.tsx     # --web-ui shadcn
src/lib/utils.ts                 # --web-ui shadcn
worker/db/schema.ts              # --web-db drizzle-d1
```

For single-project web init, the template replaces the scaffold repo's Python
`tests/` tree before copying the web Vitest tests. That prevents generated web
repos from inheriting Harness Toolkit's own test suite.

## Task contract

The generated `.mise/tasks/*` dispatch to web-native tooling:

```bash
mise run setup      # npm install --package-lock=false
mise run fmt        # prettier --write
mise run lint       # eslint
mise run typecheck  # tsc --noEmit
mise run test       # vitest run
mise run build      # vite build
mise run check      # fmt-check + lint + typecheck + test
mise run verify     # check + build + wrangler deploy --dry-run
mise run dev        # build + wrangler dev --local --port 8787
```

CI smoke coverage includes `--stack web`, so the scaffold repo verifies that a
fresh generated web project can initialize successfully.

## Cloudflare shape

The generated `wrangler.jsonc` includes:

- `assets.directory = "./dist"`
- `assets.binding = "ASSETS"`
- a D1 binding named `DB`
- `workers_dev = true`

The Worker includes:

- `GET /api/health`
- `GET /api/runs/mine`
- `POST /api/runs`

Saved runs use a generic relational table:

- `id`
- `owner_id`
- `title`
- `lineup_json`
- `result_json`
- `created_at`

The default `--web-db d1` generated Worker uses raw D1 prepared statements.
The optional `--web-db drizzle-d1` variant keeps the same Cloudflare binding and
migration, but performs reads/writes through `drizzle-orm/d1`.

The saved-run routes now require a real authenticated owner outside localhost.
In deployed environments, requests return `401` until the app wires a validated
auth provider; the template does not trust caller-supplied identity headers by
default.

## What is intentionally stubbed

The web stack does not pretend to know final production choices for every app.
It leaves these as explicit app-level follow-ups:

- production D1 database id
- Cloudflare Access policy or app-native auth provider
- custom domain or Worker route
- R2 buckets for larger object storage
- Vercel deployment alternative
- Postgres provider if the app chooses conventional relational hosting outside
  Cloudflare

The default recommendation remains Cloudflare-native for simple apps that want
one deploy surface: Worker compute, static hosting, D1 relational persistence,
and a deliberately wired auth provider.

## Known follow-ups for the template

Useful next improvements:

- add a generated "launch/deploy" how-to to every web app
- add an optional `--auth cloudflare-access` mode once the auth shape settles
- add optional `--persistence none|d1` once non-persistent marketing/tool apps
  are common
- add a `--port` override for `mise run dev`
- consider an explicit `npm audit` task so dependency audit findings are visible
  but do not surprise the main quality gate
