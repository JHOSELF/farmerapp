from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from ..db import get_session
from ..models.marketplace import User, Listing, Order
from ..schemas.market import (
	UserCreate, UserRead,
	ListingCreate, ListingRead,
	OrderCreate, OrderRead, PriceSuggestion,
)
from ..services.pricing import suggest_price

router = APIRouter()


@router.post("/users", response_model=UserRead)
def create_user(user: UserCreate) -> UserRead:
	with get_session() as session:
		model = User(name=user.name, phone=user.phone, role=user.role)
		session.add(model)
		session.commit()
		session.refresh(model)
		return UserRead.model_validate(model)


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int) -> UserRead:
	with get_session() as session:
		model = session.get(User, user_id)
		if not model:
			raise HTTPException(status_code=404, detail="User not found")
		return UserRead.model_validate(model)


@router.post("/listings", response_model=ListingRead)
def create_listing(listing: ListingCreate) -> ListingRead:
	with get_session() as session:
		if not session.get(User, listing.seller_id):
			raise HTTPException(status_code=404, detail="Seller not found")
		model = Listing(
			crop_name=listing.crop_name,
			quantity_kg=listing.quantity_kg,
			price_per_kg=listing.price_per_kg,
			location=listing.location,
			seller_id=listing.seller_id,
		)
		session.add(model)
		session.commit()
		session.refresh(model)
		return ListingRead.model_validate(model)


@router.get("/listings", response_model=list[ListingRead])
def list_listings(crop_name: str | None = None, location: str | None = None) -> list[ListingRead]:
	with get_session() as session:
		query = select(Listing)
		if crop_name:
			query = query.where(Listing.crop_name.ilike(f"%{crop_name}%"))
		if location:
			query = query.where(Listing.location.ilike(f"%{location}%"))
		models = list(session.scalars(query))
		return [ListingRead.model_validate(m) for m in models]


@router.post("/orders", response_model=OrderRead)
def create_order(order: OrderCreate) -> OrderRead:
	with get_session() as session:
		listing = session.get(Listing, order.listing_id)
		buyer = session.get(User, order.buyer_id)
		if not listing:
			raise HTTPException(status_code=404, detail="Listing not found")
		if not buyer:
			raise HTTPException(status_code=404, detail="Buyer not found")
		if order.quantity_kg > listing.quantity_kg:
			raise HTTPException(status_code=400, detail="Insufficient quantity available")

		model = Order(
			listing_id=listing.id,
			buyer_id=buyer.id,
			quantity_kg=order.quantity_kg,
			price_per_kg=listing.price_per_kg,
		)
		session.add(model)
		# Decrease available amount
		listing.quantity_kg = max(0.0, listing.quantity_kg - order.quantity_kg)
		session.commit()
		session.refresh(model)
		return OrderRead.model_validate(model)


@router.get("/price_suggestion", response_model=PriceSuggestion)
def price_suggestion(crop_name: str, location: str | None = None) -> PriceSuggestion:
	price, low, high, source = suggest_price(crop_name, location)
	return PriceSuggestion(
		crop_name=crop_name,
		location=location,
		suggested_price_per_kg=price,
		low=low,
		high=high,
		source=source,
	)