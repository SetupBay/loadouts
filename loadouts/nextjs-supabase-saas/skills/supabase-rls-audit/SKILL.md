---
name: supabase-rls-audit
description: Audit Supabase row level security. Use when asked to check database security, before launch, after adding tables, or when someone worries that users can see each other's data.
---

# Supabase RLS audit

Goal: find every way a signed-in or anonymous user could read or change rows they should not,
and report it in plain English with a fix for each.

## 1. Collect the facts
Use whichever source is available, in this order:
1. The Supabase MCP server (read-only) — run the SQL below with its query tool.
2. A local database: `supabase db dump --local --schema public` or `psql` against the local URL.
3. The migration files in `supabase/migrations/` (read them in order; later files win).

```sql
-- Tables in exposed schemas and whether RLS is on
select n.nspname as schema, c.relname as table, c.relrowsecurity as rls_enabled, c.relforcerowsecurity as rls_forced
from pg_class c join pg_namespace n on n.oid = c.relnamespace
where c.relkind = 'r' and n.nspname in ('public')
order by 1, 2;

-- Every policy
select schemaname, tablename, policyname, cmd, roles, qual as using_expr, with_check
from pg_policies where schemaname in ('public')
order by tablename, cmd;

-- Views (they bypass RLS unless created with security_invoker)
select table_schema, table_name from information_schema.views where table_schema = 'public';

-- Security definer functions callable through the API
select p.proname, p.prosecdef, p.proconfig
from pg_proc p join pg_namespace n on n.oid = p.pronamespace
where n.nspname = 'public' and p.prosecdef;
```

## 2. Check each table against these rules
Flag as **Critical**:
- RLS disabled on any table in `public`.
- A policy for `anon` or `public` roles that is `using (true)` on a table holding user data.
- An `update` policy without `with check`, letting users move rows to another owner.
- A view in `public` without `security_invoker = true` that selects from a protected table.

Flag as **High**:
- RLS enabled but no policies (the app is probably using the secret key to get round it — find out where).
- Policies that trust a column the user can write (for example `role` or `is_admin` on their own profile row).
- `security definer` functions without `set search_path = ''`.
- Storage buckets that are public but hold private uploads.

Flag as **Medium**:
- Bare `auth.uid()` instead of `(select auth.uid())` (performance, not security).
- Policy columns without indexes.

## 3. Check the app code
- Search for the secret / service role key: `grep -rn "SERVICE_ROLE\|sb_secret_" --include=*.ts --include=*.tsx .`
  Any hit outside server-only files is **Critical**.
- Check that no `NEXT_PUBLIC_` variable holds a secret.

## 4. Report
Write a short report:

```
RLS audit — <date>
Critical: <n>  High: <n>  Medium: <n>

[Critical] public.invoices — RLS is disabled. Anyone with the publishable key can read every invoice.
Fix: new migration with `alter table public.invoices enable row level security;` and an owner-only select policy.
```

Then offer to write the fix as a **new migration**. Do not apply changes to a remote database yourself.
