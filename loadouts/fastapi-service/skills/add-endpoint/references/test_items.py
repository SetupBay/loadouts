"""Tests for the items router: success, 404, 422, with the store swapped by a dependency override."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.items import ItemStore, get_store


@pytest.fixture
def client():
    store = ItemStore()
    app.dependency_overrides[get_store] = lambda: store
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_create_and_read(client):
    r = client.post("/items", json={"name": "Tea", "price_pence": 250})
    assert r.status_code == 201
    item = r.json()
    assert item == {"id": 1, "name": "Tea", "price_pence": 250}
    assert client.get(f"/items/{item['id']}").json() == item


def test_missing_item_is_404(client):
    assert client.get("/items/999").status_code == 404


def test_invalid_input_is_422(client):
    assert client.post("/items", json={"name": "", "price_pence": -1}).status_code == 422
