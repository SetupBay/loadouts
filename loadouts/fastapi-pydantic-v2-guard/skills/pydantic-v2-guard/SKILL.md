---
name: pydantic-v2-guard
description: Check a FastAPI project for Pydantic v1 models, config, validators and methods, and for Optional fields that became required, before saying a model or endpoint change is done. Use after writing or editing Pydantic models or FastAPI routes, when FastAPI raises PydanticV1NotSupportedError, Pydantic warns PydanticDeprecatedSince20, or when porting older FastAPI snippets.
---

# Pydantic v2 guard for FastAPI

Agents still write Pydantic v1 into FastAPI services: `class Config`, `orm_mode`, `@validator`, `.dict()`,
`parse_obj`. On Pydantic 2.14 most of that still runs with a `PydanticDeprecatedSince20` warning, so it looks fine
until v3 removes it. Some of it doesn't run at all: `Field(regex=)` and `from pydantic import BaseSettings` fail at
import, and FastAPI 0.162 refuses `pydantic.v1` models. And `Optional[str]` with no default became a required field.

## 1. Confirm the versions
- `uv run python -c "import pydantic, fastapi; print(pydantic.VERSION, fastapi.__version__)"` should print `2.x` and
  a current FastAPI. If Pydantic is 1.x, stop and ask before migrating anything.

## 2. Scan
```bash
python3 .agents/skills/pydantic-v2-guard/scripts/pydantic_v2_guard.py app tests
```
(Use the path the skill was installed to: `.claude/skills/...` for Claude Code, `.agents/skills/...` for the others.)

- Every `error` line is Pydantic v1 (or a deprecated FastAPI pattern). Fix it with the replacement the line gives.
  `references/migration-table.md` has the table with before/after code.
- `optional-no-default` warnings: decide whether the field may be left out. If yes, add `= None`. If clients must
  send it (possibly as `null`), keep it required and add `# guard: ok` to the line. That silences warnings, never errors.
- Run it again until it prints `0 error(s)`.

## 3. Let Pydantic check it
```bash
uv run pytest -q -W error::pydantic.warnings.PydanticDeprecatedSince20
```
- That turns every remaining v1 call into a failing test, including ones inside helpers the scanner can't see.
- For each changed model, add or keep one test that posts a payload missing each optional field, and one that checks
  the response doesn't include fields the response model leaves out.

## 4. Fixes that need care
- **Validators**: `@field_validator` needs `@classmethod`. `pre=True` becomes `mode="before"`. A `values` argument
  becomes `info: ValidationInfo` with `info.data`.
- **`from_orm`**: needs `from_attributes=True` in `model_config`. Then `Model.model_validate(orm_obj)`.
- **Aliases**: `allow_population_by_field_name` becomes `populate_by_name=True`. Check `by_alias=True` where JSON
  uses the alias.
- **Settings**: `class Config: env_file = ".env"` becomes `model_config = SettingsConfigDict(env_file=".env")`.

## 5. Report
Say how many v1 constructs you replaced, which fields changed between required and optional, and that the scanner and
the tests (with PydanticDeprecatedSince20 as an error) were clean.
