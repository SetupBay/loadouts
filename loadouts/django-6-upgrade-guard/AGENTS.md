# AGENTS.md: Django 6 project (old Django guard)

This project runs **Django 6.1** on Python 3.12 or later. Much of the Django code you remember is from 2.x–4.x,
and Django has removed a lot since then: `url()`, `ugettext`, `force_text`, `is_ajax()`, `index_together`,
`NullBooleanField`, and in 6.0 and 6.1 `CheckConstraint(check=)`, positional `Model.save()` arguments and more.

## Version facts
- Check the pin first: `uv run python -m django --version`.
- Django 6.0 needs Python 3.12+, defaults `DEFAULT_AUTO_FIELD` to `BigAutoField`, and assumes `https` in
  `forms.URLField`. It also adds built-in CSP support, template partials and a background Tasks framework (`django.tasks`).
- Django 6.1 removes the 5.2 deprecations, for example `finders.find(all=)` → `find_all=`, and
  `ArrayAgg(ordering=)` → `order_by=`. `login(request, None)` no longer falls back to `request.user`.
- Django 6.1 deprecates the `EMAIL_*` connection settings: configure mail in `MAILERS`
  (`{"default": {"BACKEND": ..., "OPTIONS": {...}}}`), in the same style as `DATABASES` and `CACHES`.
- Django 6.1 adds fetch modes: `Order.objects.fetch_mode(models.FETCH_RAISE)` turns a lazy load (an N+1) into an
  error, and `FETCH_PEERS` loads the field for every instance from the same query at once.
- Deprecation warnings for the next removals are `RemovedInDjango70Warning`, then `RemovedInDjango2028Warning`
  (the class name says which release removes them).
- If you're not sure an API exists, check the docs for this version (https://docs.djangoproject.com/en/6.1/) and
  the release notes, not old tutorials.

## Rules
- Write Django 6 code only. The `django-6-guard` skill has the full table. The common ones are: `path()` /
  `re_path()`, `gettext_lazy`, `force_str`, `CheckConstraint(condition=)`, `save(update_fields=[...])` with keywords,
  `Meta.indexes`, `BooleanField(null=True)`, `{% load static %}`, `datetime.UTC` / `zoneinfo`.
- Run `django-upgrade --target-version 6.1` on files you change. It rewrites many old forms safely.
- Every model change comes with a migration made by `makemigrations`. Never write or edit migrations by hand to "fix" a check.
- For simple background jobs, look at `django.tasks` before adding Celery, and ask the human.
- Don't change the Django version or `DEFAULT_AUTO_FIELD` in an existing project without asking.

## Before you say "done"
1. Run the `django-6-guard` scanner on the apps and templates you touched. It must report `0 error(s)`.
2. Run `django-upgrade --check --target-version 6.1` on the changed `.py` files. It must report nothing to rewrite.
3. Run `python manage.py check` and `python manage.py makemigrations --check --dry-run`.
4. Run the tests with next-version deprecations as errors:
   `python -W error::django.utils.deprecation.RemovedInDjango70Warning -W error::django.utils.deprecation.RemovedInDjango2028Warning manage.py test`.
