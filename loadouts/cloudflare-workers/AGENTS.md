# AGENTS.md: Cloudflare Workers

TypeScript Worker deployed with Wrangler. Config is in `wrangler.jsonc` (or `wrangler.toml` in older projects).

## Commands
- Local dev: `npx wrangler dev`. Logs from a deployed Worker: `npx wrangler tail`.
- After changing bindings or config: `npx wrangler types` to regenerate the `Env` types, then `npx tsc --noEmit`.
- Tests: `npx vitest run` with `@cloudflare/vitest-pool-workers` if configured.
- Done means: types regenerated if bindings changed, type-check and tests pass, and the route works under `wrangler dev`.

## Never without the human asking in this session
- `npx wrangler deploy`, `wrangler versions deploy` or any command with `--remote` against production data.
- `wrangler d1 migrations apply <db> --remote`, `wrangler kv` writes or `wrangler r2 object` writes on production namespaces.
- Changing `compatibility_date`, routes, custom domains or account settings.

## Runtime rules
- No request data in module scope. Isolates are reused across requests; globals leak between users.
- Use bindings (KV, D1, R2, Queues, Durable Objects, service bindings) from `env`, not the REST API with a token.
- Background work after the response goes in `ctx.waitUntil(promise)`. Never leave a promise floating.
- D1: always `env.DB.prepare(sql).bind(...)`; never interpolate values into SQL. Schema changes are migration files
  (`npx wrangler d1 migrations create <db> <name>`), applied with `--local` first.
- Large bodies: stream them; do not buffer whole files in memory.
- Node APIs need the `nodejs_compat` compatibility flag. Check before importing `node:*` modules.
- Validate input and return proper status codes and `Content-Type`. Set CORS headers only for listed origins.

## Secrets
- Secrets with `npx wrangler secret put <NAME>`; local values in `.dev.vars`, which stays gitignored.
- Never put secrets in `vars` in `wrangler.jsonc`, in code or in test fixtures.

## Docs
- The Cloudflare docs MCP server (`cloudflare-docs`) searches current Workers, D1, R2 and Wrangler docs. Check APIs
  and limits there instead of relying on memory. New endpoints: use the `worker-endpoint` skill.
