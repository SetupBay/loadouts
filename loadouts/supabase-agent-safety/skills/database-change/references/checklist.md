# Migration checklist

- [ ] Additive where possible; destructive steps in a later migration
- [ ] RLS enabled on every new table in an exposed schema, with select/insert/update/delete policies as needed
- [ ] Policies use `(select auth.uid())`; filtered columns are indexed
- [ ] Foreign keys indexed
- [ ] New `not null` columns have a default or a backfill before the constraint
- [ ] Large-table indexes created `concurrently` (in their own migration, outside a transaction)
- [ ] Functions are `security invoker`, or `security definer` with `set search_path = ''`
- [ ] No secrets, personal data or environment-specific IDs in the SQL
- [ ] `supabase db reset` passes locally; app tests pass; advisors clean
