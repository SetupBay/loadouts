"""Customers router: async session per request, eager loads, explicit commits."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db import SessionDep
from app.models import Customer, Order

router = APIRouter(prefix="/customers", tags=["customers"])


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    total_pence: int


class CustomerIn(BaseModel):
    email: EmailStr


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    orders: list[OrderOut]


class OrderIn(BaseModel):
    total_pence: int = Field(gt=0, le=10_000_000)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_customer(body: CustomerIn, session: SessionDep) -> CustomerOut:
    customer = Customer(email=body.email, orders=[])
    session.add(customer)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "email already registered") from None
    return CustomerOut.model_validate(customer)


@router.get("")
async def list_customers(session: SessionDep, limit: int = 50) -> list[CustomerOut]:
    # One query for customers and one for all their orders, however many rows.
    stmt = select(Customer).options(selectinload(Customer.orders)).order_by(Customer.id).limit(min(limit, 200))
    customers = (await session.scalars(stmt)).all()
    return [CustomerOut.model_validate(c) for c in customers]


@router.post("/{customer_id}/orders", status_code=status.HTTP_201_CREATED)
async def add_order(customer_id: int, body: OrderIn, session: SessionDep) -> OrderOut:
    if await session.get(Customer, customer_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "customer not found")
    order = Order(customer_id=customer_id, total_pence=body.total_pence)
    session.add(order)
    await session.commit()
    return OrderOut.model_validate(order)
