---
name: worker-endpoint
description: Add an endpoint to a Cloudflare Worker using bindings from env, validated input, parameterised D1 queries, waitUntil for background work and a local check. Use when adding or changing a Worker route.
---

# Worker endpoint

1. Read `wrangler.jsonc` for bindings and flags, and the Worker's router or `fetch` handler.
2. If you need a new binding, add it to `wrangler.jsonc` and run `npx wrangler types`. Ask before creating remote
   resources (`wrangler d1 create`, `wrangler kv namespace create`).
3. Write the handler like `references/index.ts`: parse and validate input, use `env` bindings, prepared D1 statements,
   JSON responses with the right status, and `ctx.waitUntil` for work that can finish after the response.
4. If the schema changes: `npx wrangler d1 migrations create <db> <name>`, write the SQL, apply with `--local`.
5. Run `npx tsc --noEmit` and the tests. Start `npx wrangler dev` and call the route once with curl or the test client.
6. Report the route, bindings used, migrations added and check results. Do not deploy.
