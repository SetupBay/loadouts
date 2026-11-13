"""Example router: typed models, an Annotated dependency, correct status codes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price_pence: int = Field(ge=0)


class ItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price_pence: int


class ItemStore:
    """In-memory store. Replace with the project's database session dependency."""

    def __init__(self) -> None:
        self.items: dict[int, ItemPublic] = {}

    def add(self, data: ItemCreate) -> ItemPublic:
        item = ItemPublic(id=len(self.items) + 1, **data.model_dump())
        self.items[item.id] = item
        return item


_store = ItemStore()


def get_store() -> ItemStore:
    return _store


StoreDep = Annotated[ItemStore, Depends(get_store)]

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_item(data: ItemCreate, store: StoreDep) -> ItemPublic:
    return store.add(data)


@router.get("/{item_id}")
def read_item(item_id: int, store: StoreDep) -> ItemPublic:
    item = store.items.get(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item
