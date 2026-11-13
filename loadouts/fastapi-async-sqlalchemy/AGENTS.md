# AGENTS.md: FastAPI with async SQLAlchemy

FastAPI service on SQLAlchemy 2.1's asyncio extension, with Alembic for migrations and uv for packages. SQLAlchemy 2.1
needs Python 3.11 or newer and no longer installs greenlet by default: declare `sqlalchemy[asyncio]`, or async
engines fail with an ImportError about greenlet.

## Commands
- `uv sync`; add packages with `uv add` (exact pins: `"sqlalchemy[asyncio]==2.1.5"`, `aiosqlite==0.22.1` or
  `asyncpg==0.32.0`, `alembic==1.20.0`).
- Run: `uv run fastapi dev app/main.py`. Tests: `uv run pytest -q`. Lint: `uv run ruff check . && uv run ruff format --check .`.
- Migrations: `uv run alembic revision --autogenerate -m "..."`, review the file, then `uv run alembic upgrade head`
  and `uv run alembic check`.

## Rules
- Async all the way: `create_async_engine`, `async_sessionmaker(engine, expire_on_commit=False)`, `AsyncSession`
  via a `SessionDep` dependency. No sync `Session`, `requests` or blocking file I/O inside `async def` routes.
- One session per request. Never share an `AsyncSession` across tasks (`asyncio.gather` over one session is a bug).
- Relationships use `lazy="raise"`. Load what you return with `selectinload` or `joinedload`. A `MissingGreenlet`
  error means a lazy load slipped through; fix the query, do not wrap it in `run_sync`.
- Commit explicitly in the route or service; roll back and map `IntegrityError` to 409.
- Return Pydantic response models, never ORM objects. Pydantic v2 only.
- Database URLs and passwords come from the environment (`DATABASE_URL`), never `alembic.ini` or code.
- Dispose of the engine in the app's `lifespan` shutdown.
- Never edit a migration that has run outside your machine. Add a new one.

## Tests
- Async tests through `httpx.AsyncClient` and `ASGITransport` with a throwaway database per test.
- List endpoints assert their query count. New resources: use the `async-sqlalchemy-resource` skill.
