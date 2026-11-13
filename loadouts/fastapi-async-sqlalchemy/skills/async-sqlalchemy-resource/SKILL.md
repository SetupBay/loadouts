---
name: async-sqlalchemy-resource
description: Add a database-backed resource to a FastAPI app on async SQLAlchemy 2.1 (model, Alembic migration, router and async tests) without lazy-load errors or N+1 queries. Use when adding or changing tables, relationships or endpoints that read or write the database.
---

# Add an async SQLAlchemy resource

The references are a complete working set: `db.py` (engine, session factory, `SessionDep`), `models.py`,
`customers.py` (router), `0001_customers_orders.py` (migration), `alembic_env.py` (async Alembic env) and
`test_customers.py`.

## 1. Model

- Typed mappings: `Mapped[int]`, `mapped_column(...)`. `Mapped[str | None]` means nullable; plain `Mapped[str]` is
  `NOT NULL`.
- Every relationship gets `lazy="raise"`. Under asyncio an implicit lazy load fails with `MissingGreenlet`, and in
  sync code it is a hidden extra query. `raise` turns both into an immediate, obvious error.
- Index foreign keys you filter on (`index=True`). Use `ondelete=` on the foreign key, not ORM cascade alone.

## 2. Migration

```bash
uv run alembic revision --autogenerate -m "add orders"
```

Read the generated file before keeping it. Autogenerate misses renames (it emits drop plus add, which loses data),
some server defaults and enum changes. Then:

```bash
uv run alembic upgrade head
uv run alembic check          # fails if models and migrations disagree
uv run alembic downgrade -1 && uv run alembic upgrade head   # downgrade must work too
```

The env reads `DATABASE_URL` from the environment. Never write a URL with a password into `alembic.ini`.

## 3. Router

- Take the session as `session: SessionDep`. One session per request. Never store it globally or share it between
  `asyncio` tasks: an `AsyncSession` is not safe for concurrent use.
- Load what the response needs in the query: `selectinload(Customer.orders)` for collections, `joinedload` for
  many-to-one. Use `await session.scalars(select(...))`, `await session.get(...)` and `await session.commit()`.
- `expire_on_commit=False` on the session factory keeps attributes readable after commit.
- Map `IntegrityError` to 409 after `await session.rollback()`. Return Pydantic models
  (`ConfigDict(from_attributes=True)`), never ORM objects.
- Need a relationship on an object you already have? `await session.refresh(obj, ["orders"])`, or
  `await obj.awaitable_attrs.orders` on relationships that are not `lazy="raise"`.

## 4. Tests

- `httpx.AsyncClient(transport=ASGITransport(app=app))` with `pytest.mark.anyio`, so tests run on the same event
  loop as the app.
- A fresh `sqlite+aiosqlite://` engine with `StaticPool` per test, and `app.dependency_overrides[get_session]`.
- Count queries with an event listener on `engine.sync_engine` and assert the number of SELECTs for list endpoints.
  That is the test that catches N+1 regressions.

## Done means

pytest, `ruff check`, `ruff format --check` and `alembic check` all pass, and the migration's downgrade works.
