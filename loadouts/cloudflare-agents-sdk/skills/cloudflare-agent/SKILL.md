---
name: cloudflare-agent
description: Build or change a stateful agent on Cloudflare with the Agents SDK (the agents npm package) - an Agent class on a Durable Object with SQL, state sync, schedules and @callable methods - and check its wrangler wiring before deploy. Use when the project imports from "agents", or the user wants a long-lived, per-user or scheduled agent on Workers.
---

# Cloudflare Agents SDK

An Agent is a class that extends `Agent` from the `agents` package. Each named instance is a Durable Object with its
own SQLite database, synced state, WebSocket connections and alarms, so it remembers things and can wake itself up.
Check the current API in the Cloudflare docs MCP server (`cloudflare-docs`) before using anything you are unsure of;
the SDK moves fast (this loadout was written against `agents` 0.30.1).

## Shape of an Agent (see `references/agent.ts`)
- `class X extends Agent<Env, State>` with `initialState`. `this.state` is synced to connected clients;
  change it only with `this.setState(...)`.
- Create tables in `onStart()` with `this.sql` tagged templates. Values in `${}` are bound parameters, never string
  concatenation.
- `@callable()` marks methods clients may call over the WebSocket. Treat every argument as untrusted: check types,
  lengths and ranges, and throw on bad input.
- `this.schedule(secondsOrDateOrCron, "methodName", payload)` runs a method later from the Durable Object alarm,
  even with no client connected. Make scheduled methods idempotent (they can run again after a failure) and pass ids,
  not whole records, in the payload.
- The Worker's `fetch` calls `routeAgentRequest(request, env)`, which serves `/agents/<kebab-class>/<name>` for HTTP
  and WebSocket; return 404 when it gives `null`. Use `getAgentByName(env.X, name)` to reach an instance from
  server code.
- Pick instance names deliberately (a user id, a room id). Never let a client choose another user's instance without
  an auth check in front of `routeAgentRequest`.

## Wiring (see `references/wrangler.jsonc`)
- `compatibility_flags` must include `nodejs_compat`. Keep `compatibility_date` fixed; change it on purpose.
- Every Agent class needs a `durable_objects.bindings` entry whose `class_name` matches the exported class exactly,
  and SQLite storage: `"exports": { "X": { "type": "durable-object", "storage": "sqlite" } }`. Projects on the older
  `migrations` array use `new_sqlite_classes`; never `new_classes`.
- Renaming or deleting an Agent class needs an explicit exports or migrations change. Do not just rename the class:
  stored data is tied to it. Ask the human before any change that deletes a class.
- `@callable()` needs TypeScript target ES2021: extend `agents/tsconfig` (it also expects `@types/node` and `vite`)
  or set the target yourself. Do not turn on `experimentalDecorators`.

Run the wiring check before every deploy:
```bash
node .agents/skills/cloudflare-agent/scripts/check_agents_config.mjs
```
(Claude Code: `.claude/skills/...`.) It exits 1 and says what to fix when a class is unbound, has no SQLite storage,
a binding points at a missing class, `nodejs_compat` is missing, or the TypeScript target is wrong.

## Check and ship
1. `npx tsc --noEmit` (or the project's type-check script) and the wiring check pass.
2. `npx wrangler dev` and exercise the agent locally: connect, call the methods, and for schedules use a short delay.
3. `npx wrangler deploy` only when the human asks. Secrets go in with `npx wrangler secret put NAME`, never in
   wrangler.jsonc `vars` or code.

## Done means
Type-check and wiring check pass, callable inputs are validated, scheduled methods are idempotent, and the summary
says what was run locally and what was not deployed.
