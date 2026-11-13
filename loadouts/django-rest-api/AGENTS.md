# AGENTS.md: Django REST Framework API

Django project serving a JSON API with Django REST Framework (DRF). Check `pyproject.toml` or `uv.lock` for the Django
and DRF versions before using newer APIs.

## Commands
- Tests: `uv run python manage.py test` (or `uv run pytest` if pytest-django is set up).
- Checks: `uv run python manage.py check` and `uv run python manage.py makemigrations --check --dry-run`.
- Done means: tests green, no missing migrations, every new endpoint covered by the tests listed below.

## Security defaults
- `DEFAULT_PERMISSION_CLASSES` is `IsAuthenticated`. Never add `AllowAny` to an endpoint without the user asking.
- Scope data in `get_queryset()` to the requesting user or tenant: `Note.objects.filter(owner=self.request.user)`.
  Another user's object is then a 404, not a 403 that confirms it exists.
- Set ownership on the server: `perform_create(self, serializer): serializer.save(owner=self.request.user)`. Never
  trust an owner or tenant field from the request body.
- Throttle anonymous and costly endpoints (`DEFAULT_THROTTLE_CLASSES` or per-view `throttle_classes`).

## Serializers
- List `fields` explicitly. Never `fields = "__all__"` or `exclude`: a new column must not leak into the API.
- Mark server-set fields `read_only_fields`. Validate in `validate_<field>` or `validate()`, not in views.
- Nested writes only when asked; prefer separate endpoints.

## Views and queries
- `ModelViewSet` or generic views with a router; keep views thin.
- Paginate every list endpoint (`DEFAULT_PAGINATION_CLASS`).
- `select_related` / `prefetch_related` in `get_queryset()` for every relation the serializer reads. Prove it with
  `assertNumQueries` in a test.

## Tests for every endpoint
- Anonymous request rejected; owner can do the action; lists show only the user's rows; another user gets 404;
  invalid input returns 400 naming the field; list query count stays flat as rows grow. Use the `drf-endpoint` skill.
- `APITestCase` with `force_authenticate`. Test passwords and data are obviously fake.

## Secrets and settings
- `SECRET_KEY`, database URLs and API keys come from the environment. `DEBUG` defaults to off.
