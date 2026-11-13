---
name: safe-migration
description: Make a Django model change with a reviewed migration, a zero-downtime path for destructive changes and a query-count test. Use when adding, renaming or removing fields or models.
---

# Safe migration

1. Change the model. Run `uv run python manage.py makemigrations <app>` and read the generated file.
2. Show the SQL: `uv run python manage.py sqlmigrate <app> <number>`. Flag to the human anything that rewrites or locks a
   large table (adding a non-null column with a default on old databases, new indexes on big tables, type changes).
3. Destructive changes take two releases:
   - Remove a field: release 1 stops using it in code (and makes it nullable if needed); release 2 drops the column.
   - Rename: add the new field, copy data in a data migration, switch code, drop the old field later.
     Never rely on `makemigrations` guessing a rename on a production table without checking the SQL.
4. Data migrations: `RunPython(forwards, backwards)` using `apps.get_model`. Batch large updates. Always give a
   `backwards` function, or `migrations.RunPython.noop` if reversing is genuinely safe to skip.
5. Run `uv run python manage.py migrate` locally, then `makemigrations --check --dry-run` (no changes left) and tests.
6. If a list view or API touches the changed model, add a query-count test like `references/test_query_count.py`.
7. Report: migration file, SQL summary, whether it is safe to run on a live database, and the follow-up release if any.
