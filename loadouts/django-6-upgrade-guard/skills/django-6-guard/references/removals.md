# Django removals agents still write

From the Django release notes (https://docs.djangoproject.com/en/6.1/releases/). Checked against Django 6.1.2.

| Old code | Removed in | Use |
|---|---|---|
| `from django.conf.urls import url` | 4.0 | `from django.urls import path, re_path` |
| `ugettext`, `ugettext_lazy`, `ungettext` | 4.0 | `gettext`, `gettext_lazy`, `ngettext` |
| `force_text`, `smart_text` | 4.0 | `force_str`, `smart_str` |
| `request.is_ajax()` | 4.0 | `request.headers.get("x-requested-with") == "XMLHttpRequest"`, or better, the `Accept` header |
| `NullBooleanField()` | 4.0 (model field kept only for old migrations; system check `fields.E903`) | `BooleanField(null=True)` |
| `django.utils.timezone.utc`, pytz support | 5.0 | `datetime.UTC`, `zoneinfo.ZoneInfo` |
| `USE_L10N = True` | 5.0 | delete it; always on |
| `Meta.index_together` | 5.1 | `Meta.indexes = [models.Index(fields=["a", "b"])]` |
| `CheckConstraint(check=...)` | 6.0 | `CheckConstraint(condition=...)` |
| `obj.save(False, False, None, None)` | 6.0 | `obj.save(force_insert=..., update_fields=[...])` |
| `format_html("<b>fixed</b>")` with no args | 6.0 | `mark_safe("<b>fixed</b>")` or `format_html("<b>{}</b>", v)` |
| `ChoicesMeta` | 6.0 | `ChoicesType` |
| `ModelAdmin.log_deletion()`, `LogEntryManager.log_action()` | 6.0 | `log_deletions()`, `log_actions()` |
| `FORMS_URLFIELD_ASSUME_HTTPS` | 6.0 | delete it; `URLField` assumes `https` |
| `finders.find(path, all=True)` | 6.1 | `finders.find(path, find_all=True)` |
| `ArrayAgg("x", ordering=...)` (also JSONBAgg, StringAgg) | 6.1 | `order_by=...` |
| `login(request, None)` falling back to `request.user` | 6.1 | pass the user explicitly |
| `{% load staticfiles %}`, `{% load admin_static %}` | 3.0 | `{% load static %}` |

## New in 6.0 worth knowing
- `DEFAULT_AUTO_FIELD` defaults to `django.db.models.BigAutoField`.
- Python 3.12 or later only.
- Built-in Content Security Policy support (`django.middleware.csp.ContentSecurityPolicyMiddleware`, `SECURE_CSP`).
- Template partials (`{% partialdef %}` / `{% partial %}`).
- A background Tasks framework (`django.tasks`), which needs a backend to actually run tasks.
- Django 6.1: mail is configured in `MAILERS`; the `EMAIL_*` connection settings warn with
  `RemovedInDjango2028Warning`.
- Django 6.1: fetch modes (`QuerySet.fetch_mode(models.FETCH_RAISE)`, `FETCH_PEERS`, `FETCH_ONE`).
