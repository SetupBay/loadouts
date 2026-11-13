---
name: rspec-request-spec
description: Write RSpec request specs for a Rails JSON endpoint with FactoryBot, covering the happy path, validation errors, missing params and access scoping, then run rspec and rubocop-rspec. Use when adding or changing a controller action, route or API response in a Rails app tested with RSpec.
---

# Request specs for a Rails endpoint

The references hold a complete, passing set: `projects_controller.rb`, `project.rb`, `projects_factory.rb`
(goes in `spec/factories/projects.rb`), `projects_spec.rb` (goes in `spec/requests/`), `rails_helper.rb`,
`spec_helper.rb` and `rubocop.yml`.

## What every endpoint's spec covers

1. **Happy path**, with status and the body fields that matter: `response.parsed_body`, compared with `eq` or
   `include`.
2. **Validation failure**: `have_http_status(:unprocessable_content)` and the error message for the field.
3. **Missing or malformed params**: `params.expect` raises, and Rails answers 400.
4. **Scoping**: another user's record returns 404, and the list never includes it. The spec catches an unscoped
   `find`.
5. **Mass assignment**: a forbidden attribute in the body (`owner_id`, `admin`, `role`) is ignored.
6. **Side effects**: `expect { ... }.to change(Model, :count).by(n)` for creates and deletes.

## How to write them

- Request specs (`spec/requests/`), not controller specs. They go through routing, middleware and params parsing.
- Use `as: :json` for JSON bodies. With `wrap_parameters`, a flat JSON body is wrapped under the model key, so test a
  missing key with a form post.
- Use `create` only when the database is needed, and `build` or `build_stubbed` in model and unit specs. Use a
  factory `sequence` for unique fields and traits (`:archived`) for variants. Never use a fixed id.
- `let` for data an example uses. Create records inside the example when their order or count is the point.
- Follow arrange, act, assert with blank lines between, and one behaviour per example. Name examples for the
  behaviour ("hides another owner's project behind a 404"), not the implementation.
- No `sleep`, no real network and no `allow_any_instance_of`. Freeze time with `travel_to` when a time is asserted.

## Run

```bash
bundle exec rspec spec/requests/projects_spec.rb
bundle exec rspec                       # the whole suite, random order
bundle exec rubocop app spec
```

Random order is on (`config.order = :random`). If a spec fails only in some orders, it leaks state. Fix the leak;
do not pin the seed.

## Done means

The new examples fail before the change and pass after it. The whole suite and rubocop (omakase, rubocop-rspec and
rubocop-rspec_rails) are green.
