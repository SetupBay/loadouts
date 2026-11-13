---
name: drf-endpoint
description: Add a Django REST Framework endpoint with an explicit serializer, a user-scoped queryset, server-set ownership, pagination and the six tests every endpoint needs.
---

# Add a DRF endpoint

Examples: `references/serializers.py`, `references/views.py`, `references/urls.py`, `references/tests.py`.

1. Model first, if needed: add it, then `uv run python manage.py makemigrations` and check the migration.
2. Serializer: explicit `fields`, server-set fields in `read_only_fields`, validation in `validate_<field>`.
3. View: `ModelViewSet` (or a narrower generic view) with:
   - `get_queryset()` filtered to `self.request.user`, with `select_related` for relations the serializer reads
   - `perform_create()` that sets the owner
   - permissions no weaker than the project default
4. Route it with a `DefaultRouter` and `basename`.
5. Tests (`APITestCase`):
   - anonymous is rejected (401 or 403, depending on the authentication class)
   - create sets the owner from the request, ignoring an owner in the body
   - list shows only the user's own rows
   - another user's object is 404 for read, update and delete
   - invalid input is a 400 that names the field
   - `assertNumQueries` on the list endpoint with several rows
6. Run `uv run python manage.py test`, `check` and `makemigrations --check --dry-run`.
