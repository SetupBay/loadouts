# AGENTS.md: Django app

Django project managed with uv. Supported Django: 5.2 LTS or 6.x; check `pyproject.toml` before using a newer API.

## Commands
- Run: `uv run python manage.py runserver`. Shell: `uv run python manage.py shell`.
- Tests: `uv run pytest -q` (pytest-django) or `uv run python manage.py test`.
- Checks before saying done: `uv run python manage.py check`, `uv run python manage.py makemigrations --check --dry-run`
  (must report no changes), tests, and `uv run ruff check .`.
- Deployment settings: `uv run python manage.py check --deploy` with production settings.

## Models and migrations
- Every model change ships with its migration in the same commit. Use the `safe-migration` skill.
- Never edit or delete a migration that may have run anywhere else. Add a new one.
- In data migrations use `apps.get_model("app", "Model")`, never import the model class.
- Read the SQL of risky migrations with `uv run python manage.py sqlmigrate <app> <number>` and show it to the human.

## Queries
- No N+1: `select_related` for foreign keys, `prefetch_related` for reverse and many-to-many. Prove it with
  `assertNumQueries` (or `django_assert_num_queries` in pytest-django) when you touch a list view.
- Writes that must succeed together go in `transaction.atomic()`.
- Never build SQL with string formatting. Use the ORM, or `raw()` and `cursor.execute()` with parameters.

## Security
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` and database credentials come from the environment, never hard-coded.
- Never add `@csrf_exempt` to a view that uses session auth. Never mark user input `mark_safe` or `|safe`.
- Validate input with forms or serializers, not by reading `request.POST` directly.
- Views that need a login use `LoginRequiredMixin` or `@login_required`; check object ownership in the queryset.

## Style
- Fat models, thin views: business rules on the model or in a service module, not in templates.
- Settings changes go in the settings module the project already uses; do not add a second settings system.
