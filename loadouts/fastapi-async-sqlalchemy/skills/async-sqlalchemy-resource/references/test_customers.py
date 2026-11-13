"""Async API tests: httpx.AsyncClient over ASGITransport, a fresh in-memory database
per test, and a query counter that catches N+1 loads."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db import Base, get_session
from app.main import app
from app.models import Customer

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def db() -> AsyncIterator[dict]:
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    queries: list[str] = []
    event.listen(engine.sync_engine, "before_cursor_execute", lambda *a: queries.append(a[2]))

    async def override() -> AsyncIterator:
        async with factory() as session:
            yield session

    app.dependency_overrides[get_session] = override
    yield {"factory": factory, "queries": queries}
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.fixture
async def client(db: dict) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_create_and_list_without_n_plus_one(client: AsyncClient, db: dict) -> None:
    for i in range(5):
        r = await client.post("/customers", json={"email": f"c{i}@example.com"})
        assert r.status_code == 201
        await client.post(f"/customers/{r.json()['id']}/orders", json={"total_pence": 1000 + i})
    db["queries"].clear()
    r = await client.get("/customers")
    assert r.status_code == 200
    assert [len(c["orders"]) for c in r.json()] == [1, 1, 1, 1, 1]
    selects = [q for q in db["queries"] if q.lstrip().upper().startswith("SELECT")]
    assert len(selects) == 2, selects


async def test_duplicate_email_is_409(client: AsyncClient) -> None:
    assert (await client.post("/customers", json={"email": "a@example.com"})).status_code == 201
    r = await client.post("/customers", json={"email": "a@example.com"})
    assert r.status_code == 409


async def test_order_for_missing_customer_is_404(client: AsyncClient) -> None:
    r = await client.post("/customers/999/orders", json={"total_pence": 500})
    assert r.status_code == 404


async def test_bad_total_is_422(client: AsyncClient) -> None:
    r = await client.post("/customers", json={"email": "b@example.com"})
    bad = await client.post(f"/customers/{r.json()['id']}/orders", json={"total_pence": 0})
    assert bad.status_code == 422


async def test_lazy_load_raises_instead_of_hiding_a_query(client: AsyncClient, db: dict) -> None:
    await client.post("/customers", json={"email": "lazy@example.com"})
    async with db["factory"]() as session:
        customer = (await session.scalars(select(Customer))).one()
        with pytest.raises(InvalidRequestError):
            _ = customer.orders
        await session.refresh(customer, ["orders"])
        assert customer.orders == []
