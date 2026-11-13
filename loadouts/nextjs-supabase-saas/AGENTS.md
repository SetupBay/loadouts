# AGENTS.md: Next.js + Supabase SaaS

You are working on a Next.js (App Router) SaaS backed by Supabase (Postgres, Auth, Storage).
Treat the database as production unless told otherwise.

## Stack and layout
- Next.js App Router in `app/`. TypeScript strict mode. No Pages Router code.
- Supabase clients live in `lib/supabase/`:
  - `server.ts` creates a server client with `@supabase/ssr` and the Next.js `cookies()` store.
  - `client.ts` creates a browser client. Only use it inside `"use client"` components.
  - `middleware.ts` (or `proxy.ts` on newer Next.js) refreshes the auth session cookie on each request.
- Schema lives in `supabase/migrations/`. Generated types live in `lib/database.types.ts`.

## Server vs client
- Components are Server Components by default. Add `"use client"` only for state, effects or browser APIs.
- Fetch data in Server Components or Route Handlers, not in `useEffect`, unless it is genuinely live data.
- Mutations go through Server Actions or Route Handlers. Validate every input with `zod` on the server,
  even if the form validated it already.
- Never import `lib/supabase/server.ts` or anything using secret env vars from a client component.

## Auth
- Get the user on the server with `supabase.auth.getUser()` (it verifies the JWT with Supabase).
  Do not trust `getSession()` on the server for authorisation decisions.
- Protect pages by checking the user in the layout or page, and redirect if missing. Middleware alone is not enough.
- Authorisation belongs in RLS policies. App code checks are a convenience, not the security boundary.

## Keys and environment
- `NEXT_PUBLIC_SUPABASE_URL` and the publishable (anon) key are safe in the browser *only because RLS is on*.
- The secret / `service_role` key bypasses RLS. It must only be used in server-only code for admin jobs,
  never prefixed `NEXT_PUBLIC_`, never logged, never committed.
- Keep `.env.local` out of git. Add any new variable to `.env.example` with a dummy value.

## Database changes
- Every schema change is a new migration: `supabase migration new <name>`. Never edit an applied migration.
- Every new table in an exposed schema gets `alter table ... enable row level security;` in the same migration,
  plus explicit policies for each operation it needs (select, insert, update, delete).
- Prefer `(select auth.uid())` in policies over bare `auth.uid()` so Postgres can cache it per statement.
- Add indexes on columns used in policies (for example `user_id`, `org_id`).
- After a schema change, regenerate types: `supabase gen types typescript --local > lib/database.types.ts`.

## Payments (if present)
- Stripe webhooks are verified with the signing secret before any database write.
- Entitlements (plan, seats) are written by the webhook handler, never by the client.

## Before you say "done"
1. `npm run lint` and `npm run build` pass.
2. No secret key reachable from client bundles (`grep -r SERVICE_ROLE app components` is empty).
3. Any new table has RLS enabled and at least one policy. Run the `supabase-rls-audit` skill if unsure.
4. Summarise what changed, any migration added, and anything the human must do (env vars, dashboard settings).

## Do not
- Do not disable RLS to "make it work". Fix the policy instead.
- Do not run destructive SQL (`drop`, `truncate`, `delete` without `where`) against a remote project.
- Do not add a new auth library. Supabase Auth is the auth system.
