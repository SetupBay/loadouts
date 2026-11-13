# AGENTS.md: Rails app tested with RSpec

A Rails 8.1 app whose tests are RSpec (`rspec-rails`) with FactoryBot. Check `Gemfile.lock` for exact versions before
using an API.

## Commands
- Tests: `bundle exec rspec` (random order). One file: `bundle exec rspec spec/requests/projects_spec.rb:42`.
- Lint: `bundle exec rubocop` (rubocop-rails-omakase plus rubocop-rspec and rubocop-rspec_rails).
- Migrations: `bin/rails db:migrate`, then commit `db/schema.rb`. The test database follows the schema
  (`maintain_test_schema!`).
- Done means: the new specs fail without the change and pass with it, and the whole suite and rubocop are green.

## Rules
- Every controller action has request specs (`spec/requests/`): the happy path, the validation error (422,
  `:unprocessable_content`), missing params (400), and another user's record (404). Use the `rspec-request-spec`
  skill.
- Strong params with `params.expect(model: [...])`. Never permit ownership or role fields. Set them from the
  authenticated user.
- Scope every lookup to the current user or account (`current_user.projects.find(...)`). An unscoped `Model.find`
  in a controller is a bug.
- Model specs for validations and scopes use `build` or `build_stubbed`, and hit the database only when the
  behaviour needs it.
- FactoryBot factories hold the minimum valid record. Variants go in traits. Unique fields use `sequence`.
- No controller specs, no `allow_any_instance_of`, no `sleep`, no real HTTP in specs.
- Do not change `.rspec`, `spec_helper.rb` or `rails_helper.rb` to make a failing spec pass.
