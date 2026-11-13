"""Customer and Order. Relationships use lazy="raise" so a missed eager load fails loudly."""

from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    orders: Mapped[list["Order"]] = relationship(back_populates="customer", lazy="raise")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    total_pence: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    customer: Mapped[Customer] = relationship(back_populates="orders", lazy="raise")
