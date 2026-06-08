---
id: web-stack
title: Web Stack
description: >
  Web stack tooling: Vite and React for the browser app, Cloudflare Workers for
  API routes and hosting, D1 migrations for relational persistence, and
  Prettier, ESLint, TypeScript, and Vitest for validation.
index:
  - id: tools
    keywords: [vite, react, cloudflare, workers, d1, npm, wrangler]
  - id: generated-layout
    keywords: [layout, worker, migrations, saved-runs, auth]
  - id: task-contract
    keywords: [fmt, lint, typecheck, test, build, verify]
  - id: cloudflare-bindings
    keywords: [wrangler, assets, d1, database, hosting]
---

# Web Stack

## Tools

| Purpose | Tool | Config |
|---------|------|--------|
| Package management | npm | `package.json` |
| Browser app | Vite + React | `vite.config.ts` |
| API and hosting | Cloudflare Workers + Static Assets | `wrangler.jsonc` |
| Relational persistence | Cloudflare D1 | `migrations/` |
| Formatter | Prettier | `package.json` scripts |
| Linter | ESLint flat config | `eslint.config.mjs` |
| Type checker | TypeScript | `tsconfig.json` |
| Test runner | Vitest | `vitest.config.ts` |

The generated stack targets Node 22 through `.mise.toml` and installs npm
dependencies during `mise run setup`.

## Generated layout

```
my-dashboard/
├── package.json
├── wrangler.jsonc
├── index.html
├── src/                    # React app
├── worker/                 # Cloudflare Worker API routes
├── migrations/             # D1 schema migrations
├── tests/                  # Vitest coverage
└── public/                 # Static assets and seed data
```

The worker includes a small `/api/health` route and saved-run endpoints:

- `GET /api/runs/mine`
- `POST /api/runs`

The saved-run table is intentionally generic: an owner id, a title, a lineup
JSON blob, a result JSON blob, and timestamps. That gives web apps such as the
NBA simulator a relational home for login-owned saved runs without committing
the template to a specific auth provider.

## Task contract

```bash
mise run setup      # npm install --package-lock=false
mise run fmt        # prettier --write on app/worker/test/config files
mise run lint       # eslint src worker tests vite/vitest configs
mise run typecheck  # tsc --noEmit
mise run test       # vitest run
mise run build      # vite build
mise run check      # fmt-check + lint + typecheck + test
mise run verify     # check + build + wrangler deploy dry-run
```

`mise run test` writes `test-results/vitest.txt` for CI artifact upload.

## Cloudflare bindings

Generated `wrangler.jsonc` includes:

- `assets.directory = "./dist"` and `assets.binding = "ASSETS"` for the Vite
  static build
- a D1 binding named `DB`
- `workers_dev = true` for first deploys before a custom domain is configured

Custom domains, production D1 database ids, Cloudflare Access, and external
auth providers are intentionally left as follow-up configuration. The template
keeps those boundaries explicit instead of faking a provider-specific setup.
