# AGENTS.md: Rails app

Ruby on Rails app. Check `Gemfile.lock` for the Rails version before using newer APIs; these rules assume Rails 8.

## Commands
- Tests: `bin/rails test` (and `bin/rails test:system` if system tests exist). Single file:
  `bin/rails test test/models/order_test.rb`.
- Lint: `bin/rubocop` (rubocop-rails-omakase in new apps). Security: `bin/brakeman --no-pager`.
- Migrations: `bin/rails db:migrate`, then confirm `bin/rails db:rollback` and migrate again work.
- Done means: tests green, rubocop clean, brakeman shows no new warnings, `db/schema.rb` changed only by migrations.

## Models and the database
- Every schema change is a migration generated with `bin/rails generate migration`. Never edit `db/schema.rb` by hand.
- Migrations are reversible (`change` with reversible operations, or `up` and `down`). No data backfills in schema
  migrations on large tables; write a separate task or job.
- Constraints in the database as well as the model: `null: false`, foreign keys, unique indexes behind
  `validates ... uniqueness`.
- If `strong_migrations` is in the Gemfile, follow its advice instead of silencing it.
- Avoid N+1 queries: `includes` or `preload` for associations used in loops. Prove it with `assert_queries_count`.
- Money in integer minor units or `decimal`, never `float`.
- New model or column: use the `rails-model-change` skill.

## Controllers and views
- Strong parameters with `params.expect(order: [:title, :quantity])` (Rails 8) or `require`/`permit`. Never
  `permit!`.
- Keep controllers to the seven REST actions where possible; add a new controller rather than custom actions.
- Escape output: no `html_safe` or `raw` on user content. Use `sanitize` with an allow-list if HTML is required.
- Authorise every record lookup through the current user (`current_user.orders.find(params[:id])`).

## Secrets and config
- Credentials live in `config/credentials.yml.enc`, edited with `bin/rails credentials:edit`. Never commit
  `config/master.key` or print credentials.
- Do not run commands against production (`RAILS_ENV=production`, `kamal`, `cap`) unless the user asks.

## Dependencies
- Ask before adding a gem. Add it with `bundle add <gem> --version "~> x.y"` and commit `Gemfile.lock`.
