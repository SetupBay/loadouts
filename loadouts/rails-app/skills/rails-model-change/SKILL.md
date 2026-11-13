---
name: rails-model-change
description: Add or change a Rails model with a reversible migration, database constraints, validations, an N+1-safe query scope and a model test. Use for new tables, new columns and new associations.
---

# Rails model change

Examples: `references/20261017120000_create_orders.rb`, `references/order.rb`, `references/order_test.rb`.

1. Generate, do not hand-write the file name: `bin/rails generate migration CreateOrders` (or `AddXToY`).
2. In the migration:
   - `null: false` on required columns, with a default where it makes sense.
   - `t.references ... foreign_key: true` for associations.
   - A unique index for anything validated as unique.
   - Money as integer pence (`price_pence`) or `decimal` with precision and scale.
3. Run `bin/rails db:migrate`, then `bin/rails db:rollback` and `bin/rails db:migrate` again. Both directions must work.
   Commit the `db/schema.rb` change the migration produced.
4. Model: validations that mirror the constraints, associations with `dependent:` chosen on purpose, and scopes that
   preload what callers will use.
5. Test in `test/models/`: one test per validation, one for each scope, and an `assert_queries_count` test for any
   scope that should avoid N+1 queries.
6. Run `bin/rails test test/models/<model>_test.rb`, then the full suite and `bin/rubocop`.
