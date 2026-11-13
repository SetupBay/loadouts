# AGENTS.md (repository root)

Monorepo: `apps/web` (React + Vite), `apps/api` (Fastify), `packages/shared` (types and zod schemas). Turborepo + pnpm workspaces.
Each app has its own `AGENTS.md` with its commands; read the one nearest to the files you change.

## Commands (from the root)
- Install: `pnpm install --frozen-lockfile`
- Everything: `pnpm turbo run build test lint`
- One package: `pnpm --filter @acme/api test`

## Rules for every package
- Shared types live in `packages/shared`; never copy a type into an app
- A change to `packages/shared` must build and test every app that depends on it: `pnpm turbo run test --filter=...@acme/shared`
- Add dependencies to the package that uses them, never to the root `package.json`
- One concern per pull request; do not mix a refactor with a feature

## Never
- Edit generated files (`**/dist/`, `apps/api/src/generated/`)
- Change CI (`.github/`) or Turborepo config without asking
