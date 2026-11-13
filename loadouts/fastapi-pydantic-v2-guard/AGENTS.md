# AGENTS.md: FastAPI on Pydantic v2 (Pydantic v1 guard)

This is a **FastAPI** service on **Pydantic v2** (`pydantic>=2.14,<3`, `fastapi>=0.162`). Much of the FastAPI code
you remember was written for Pydantic v1. Some of it fails at import, some only warns, and one pattern changes
whether a field is required.

## Version facts
- Check the pins first: `uv pip show fastapi pydantic pydantic-settings`.
- Current FastAPI refuses `pydantic.v1` models outright (`PydanticV1NotSupportedError`). There is no v1 fallback.
- v1 methods such as `.dict()`, `@validator` and `class Config` still run on v2 but warn
  `PydanticDeprecatedSince20`. They are removed in Pydantic v3. Treat them as errors here.
- `Optional[int]` with no default is a **required** field in v2. It allows `None`, it doesn't make the field optional.
- Settings live in `pydantic-settings`: `from pydantic_settings import BaseSettings, SettingsConfigDict`.
- If you're not sure an API exists in v2, check the migration guide (https://docs.pydantic.dev/latest/migration/)
  instead of guessing.

## Rules
- Write Pydantic v2 only. The `pydantic-v2-guard` skill has the full table. The common ones are:
  `model_config = ConfigDict(from_attributes=True)` (not `class Config: orm_mode = True`),
  `@field_validator` / `@model_validator` (not `@validator` / `@root_validator`), `model_dump()` /
  `model_dump_json()` / `model_validate()` (not `dict()` / `json()` / `parse_obj()`), `Field(pattern=)` (not `regex=`),
  `min_length` (not `min_items`), `Literal[...]` (not `const=`).
- Give every optional field a default: `note: str | None = None`.
- Separate request and response models. Set `response_model` (or a return annotation) so output is filtered.
- Startup and shutdown go in a `lifespan` function, not `@app.on_event`.
- Don't add `pydantic.v1` imports or downgrade Pydantic to make old code pass.

## Before you say "done"
1. Run the `pydantic-v2-guard` scanner on the files you touched. It must report `0 error(s)`. Read every `warn`.
2. Run the tests with v1 deprecations as errors:
   `uv run pytest -q -W error::pydantic.warnings.PydanticDeprecatedSince20`.
3. Say which models changed shape (required/optional fields, aliases) so API clients can be checked.
