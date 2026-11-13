# AGENTS.md (apps/api)

Fastify 5 API on Node 24. Postgres via Kysely. Read the root `AGENTS.md` first; this file adds API rules.

## Commands (from apps/api)
- Dev: `pnpm dev` (port 4000) · tests: `pnpm test` · one: `pnpm test src/routes/orders.test.ts`
- Migrations: `pnpm migrate:new <name>` creates a file in `migrations/`; `pnpm migrate:up` runs them locally only

## Rules
- Every route declares a zod schema from `@acme/shared` for body, params and response
- Handlers stay thin: validation and HTTP in `src/routes/`, logic in `src/services/` with unit tests
- Errors use `httpErrors` from `@fastify/sensible`; never leak stack traces or SQL to clients
- Queries are parameterised through Kysely; no string-built SQL

## Never
- Run migrations against anything but your local database
- Return database rows straight to clients; map them to the shared response schema

## Done means
`pnpm test` passes here and in `apps/web` if you changed a shared schema, and you called the changed route locally
with a real request and saw the expected response.
