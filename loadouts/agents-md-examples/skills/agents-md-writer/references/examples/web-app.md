# AGENTS.md

Next.js 16 (App Router) + TypeScript strict + Postgres via Drizzle. pnpm only.

## Commands
- Install: `pnpm install --frozen-lockfile`
- Dev server: `pnpm dev` (http://localhost:3000; reuse a running one, check `.next/dev/lock`)
- Type check: `pnpm typecheck`
- Lint and format: `pnpm lint` then `pnpm format`
- Unit tests: `pnpm test` · one file: `pnpm test src/lib/price.test.ts`
- End-to-end: `pnpm e2e` (needs the dev server)
- DB migration: `pnpm db:generate` writes SQL to `drizzle/`; never run `db:push` against a shared database

## Layout
- `app/` routes; server components by default, `"use client"` only for interactivity
- `src/lib/` pure logic with unit tests next to it; `src/db/` schema and queries; `src/components/` UI

## Conventions
- Server actions validate input with zod and return `{ ok, error }`; never throw to the client
- Money is integer pence; dates are UTC `Date` objects, formatted only in components
- New UI uses the existing components in `src/components/ui/`; no new UI libraries

## Never
- Commit `.env*` files or print secrets; add new variables to `.env.example` with a dummy value
- Edit `drizzle/` migrations that are already merged; write a new one
- Disable a lint rule or a test to get green

## Done means
`pnpm typecheck && pnpm lint && pnpm test` pass, the changed page was opened in the browser and works, and the
PR description says what you checked by hand.
