# Pydantic v1 → v2 table for FastAPI

From the Pydantic migration guide (https://docs.pydantic.dev/latest/migration/) and FastAPI's docs. Checked against
pydantic 2.14.1, pydantic-settings 2.16.2 and fastapi 0.162.0.

## Fails on v2 or in FastAPI

| v1 | v2 | What happens with v1 code |
|---|---|---|
| `from pydantic.v1 import BaseModel` in a route | `from pydantic import BaseModel` | FastAPI raises `PydanticV1NotSupportedError` |
| `from pydantic import BaseSettings` | `from pydantic_settings import BaseSettings` | `PydanticImportError` |
| `Field(regex="^a")` | `Field(pattern="^a")` | `PydanticUserError: regex is removed` |
| `Field(const=True)` | `Literal["value"]` | error |
| `constr(regex=...)` | `Annotated[str, StringConstraints(pattern=...)]` | error |
| `note: Optional[str]` (no default) | `note: str \| None = None` | field is now required, so 422 for clients that leave it out |

## Deprecated (warns PydanticDeprecatedSince20, removed in v3)

| v1 | v2 |
|---|---|
| `class Config: orm_mode = True` | `model_config = ConfigDict(from_attributes=True)` |
| `allow_population_by_field_name = True` | `populate_by_name=True` |
| `schema_extra = {...}` | `json_schema_extra={...}` |
| `anystr_strip_whitespace = True` | `str_strip_whitespace=True` |
| `allow_mutation = False` | `frozen=True` |
| `@validator("x", pre=True)` | `@field_validator("x", mode="before")` + `@classmethod` |
| `@validator("x", each_item=True)` | `list[Annotated[int, AfterValidator(check)]]` |
| `@root_validator` | `@model_validator(mode="after")` (instance method) |
| `m.dict(exclude_unset=True)` | `m.model_dump(exclude_unset=True)` |
| `m.json()` | `m.model_dump_json()` |
| `M.parse_obj(d)` / `M.parse_raw(s)` | `M.model_validate(d)` / `M.model_validate_json(s)` |
| `M.from_orm(row)` | `M.model_validate(row)` with `from_attributes=True` |
| `m.copy(update={...})` | `m.model_copy(update={...})` |
| `M.schema()` | `M.model_json_schema()` |
| `M.__fields__` | `M.model_fields` |
| `M.update_forward_refs()` | `M.model_rebuild()` |
| `M.construct(...)` | `M.model_construct(...)` |
| `Field(min_items=1, max_items=5)` | `Field(min_length=1, max_length=5)` |
| `parse_obj_as(list[M], data)` | `TypeAdapter(list[M]).validate_python(data)` |

## FastAPI patterns

| Old | Current |
|---|---|
| `@app.on_event("startup")` | `@asynccontextmanager async def lifespan(app): ...; yield` and `FastAPI(lifespan=lifespan)` |
| `response_model=dict` | a response model, so output is filtered and documented |
| `Depends()` default arguments | `Annotated[Session, Depends(get_session)]` |
