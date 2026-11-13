---
name: django-6-guard
description: Check a Django project for APIs removed between Django 4.0 and 6.1, run django-upgrade and Django's own checks, before saying a Django change is done. Use after writing or editing models, views, URLs, settings or templates, when Django raises an unexpected keyword or missing attribute error, or when porting older Django snippets or tutorials.
---

# Django 6 guard

Agents trained on years of Django answers still write `url()`, `ugettext_lazy`, `force_text`, `request.is_ajax()`,
`index_together` and `{% load staticfiles %}`. All of those are gone. Django 6.0 and 6.1 removed more, including
`CheckConstraint(check=)`, positional `Model.save()` arguments, `format_html()` without arguments,
`finders.find(all=)` and the Postgres aggregates' `ordering=`. This skill finds them, lets `django-upgrade` rewrite
what it can, then lets Django check the rest.

## 1. Confirm the version
- `uv run python -m django --version` should print `6.1.x`. If it doesn't, ask before changing code for a different version.

## 2. Scan
```bash
python3 .agents/skills/django-6-guard/scripts/django6_guard.py shop templates
```
(Use the path the skill was installed to: `.claude/skills/...` for Claude Code, `.agents/skills/...` for the others.)

- Every `error` line is a removed API. Fix it with the replacement on the line. `references/removals.md` says which
  release removed each one.
- `warn` lines are behaviour changes to decide on: `login(request, None)`, an explicit `AutoField` default,
  positional mail arguments, `EMAIL_*` settings that now belong in `MAILERS`, or Celery added where `django.tasks` might do.

## 3. Let django-upgrade rewrite what it safely can
```bash
uvx --from django-upgrade==1.33.0 django-upgrade --target-version 6.1 shop/*.py
```
- Then run it again with `--check`. It must print nothing. Review its diff like any other change.
- It doesn't cover everything the scanner does (for example `NullBooleanField` or `CheckConstraint(check=)`),
  so run both.

## 4. Let Django check it
```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python -W error::django.utils.deprecation.RemovedInDjango70Warning \
       -W error::django.utils.deprecation.RemovedInDjango2028Warning manage.py test
```
- `check` reports removed fields as system-check errors (for example `fields.E903` for `NullBooleanField`).
- If `makemigrations --check` wants a migration, create it with `makemigrations` and include it in the change.

## 5. Report
Say which removed APIs you replaced, what django-upgrade rewrote, any migration you added, and that the scanner,
`check`, `makemigrations --check` and the tests were clean.
