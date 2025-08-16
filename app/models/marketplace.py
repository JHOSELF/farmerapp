from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	name: Mapped[str] = mapped_column(String(100), nullable=False)
	phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
	role: Mapped[str] = mapped_column(String(20), nullable=False, default="farmer")

	listings: Mapped[list[Listing]] = relationship("Listing", back_populates="seller")
	orders: Mapped[list[Order]] = relationship("Order", back_populates="buyer")


class Listing(Base):
	__tablename__ = "listings"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	crop_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
	quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
	price_per_kg: Mapped[float] = mapped_column(Float, nullable=False)
	location: Mapped[str] = mapped_column(String(120), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

	seller: Mapped[User] = relationship("User", back_populates="listings")
	orders: Mapped[list[Order]] = relationship("Order", back_populates="listing")


class Order(Base):
	__tablename__ = "orders"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
	buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
	price_per_kg: Mapped[float] = mapped_column(Float, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	listing: Mapped[Listing] = relationship("Listing", back_populates="orders")
	buyer: Mapped[User] = relationship("User", back_populates="orders")