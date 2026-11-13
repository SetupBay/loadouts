# AGENTS.md: FastAPI service

Python API built with FastAPI and Pydantic v2, managed with uv.

## Commands
- Install and sync: `uv sync`. Add a dependency: `uv add <package>` (never `pip install` into the project).
- Run locally: `uv run fastapi dev app/main.py`. Production entry point: `uv run fastapi run app/main.py`.
- Tests: `uv run pytest -q`. Lint and format: `uv run ruff check . && uv run ruff format --check .`.
- Types: `uv run mypy app` if mypy is configured in pyproject.toml.
- Before saying a change is done: tests, ruff check and ruff format all pass.

## Layout
- `app/main.py` creates the app and includes routers. One `APIRouter` per resource in `app/routers/`.
- Request and response models in `app/schemas/`; database models separate from API models.
- Settings in `app/config.py` with pydantic-settings `BaseSettings`, read from the environment. No values in code.

## Rules
- Dependencies with `Annotated[T, Depends(...)]`; define reusable aliases (`SessionDep`, `CurrentUser`).
- Every route declares its response type (return annotation or `response_model`) so output is validated and documented.
  Never return ORM objects or dicts with extra fields straight from a route.
- Use `async def` only when everything awaited inside is async. Blocking calls (most DB drivers, `requests`, file I/O)
  go in plain `def` routes, which FastAPI runs in a threadpool. Never call blocking code inside `async def`.
- Startup and shutdown in a `lifespan` context manager, not `@app.on_event`.
- Errors: raise `HTTPException` with the right status (404 missing, 409 conflict, 422 is automatic for bad input).
  Do not return 200 with an error body.
- Pydantic v2 only: `model_config = ConfigDict(...)`, `model_dump()`, `field_validator`. No v1 `class Config` or `.dict()`.
- Auth: check it in a dependency, not inside each route. Never log tokens, passwords or full request bodies.
- CORS: list exact origins. Never `allow_origins=["*"]` together with `allow_credentials=True`.

## Tests
- `TestClient(app)` for HTTP tests. Swap dependencies with `app.dependency_overrides[...]`, and clear them after.
- Every new route gets a happy-path test and at least one failure test (404, 422 or auth).
- New endpoints: use the `add-endpoint` skill.
