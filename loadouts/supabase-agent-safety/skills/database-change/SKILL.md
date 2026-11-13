---
name: database-change
description: Plan, write and test a Supabase Postgres schema change as a reviewed migration, using the read-only MCP server to inspect the current schema. Use for any table, column, index, policy or function change.
---

# Database change

1. **Inspect** the current schema with the `supabase` MCP tools (list tables, describe the tables involved, list policies
   and existing migrations). Confirm the server is read-only and on the dev project.
2. **Plan** in the chat: the change, whether it is additive or destructive, the policy impact, and the rollout order
   (expand → backfill → switch → contract). Wait for the human to agree if anything is destructive.
3. **Write** the migration: `supabase migration new <name>`, then fill it in. Follow `references/checklist.md`.
4. **Test locally**: `supabase start` if needed, then `supabase db reset` on the local stack, and run the app's tests.
   Test policies as each role: anonymous, an ordinary user, another user's data.
5. **Advisors**: run the security and performance advisors (MCP tool or dashboard) against the local or dev database and fix findings.
6. **Types**: regenerate generated types if the project uses them (`supabase gen types typescript --local > <path>`).
7. **Hand over**: open a PR with the migration and a short rollout note. Applying it to remote projects is the human's step.
