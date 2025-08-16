from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
	name: str
	phone: Optional[str] = None
	role: str = Field(default="farmer")


class UserRead(BaseModel):
	id: int
	name: str
	phone: Optional[str]
	role: str

	model_config = ConfigDict(from_attributes=True)


class ListingCreate(BaseModel):
	crop_name: str
	quantity_kg: float
	price_per_kg: float
	location: Optional[str] = None
	seller_id: int


class ListingRead(BaseModel):
	id: int
	crop_name: str
	quantity_kg: float
	price_per_kg: float
	location: Optional[str]
	seller_id: int

	model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
	listing_id: int
	buyer_id: int
	quantity_kg: float


class OrderRead(BaseModel):
	id: int
	listing_id: int
	buyer_id: int
	quantity_kg: float
	price_per_kg: float

	model_config = ConfigDict(from_attributes=True)


class PriceSuggestion(BaseModel):
	crop_name: str
	location: Optional[str] = None
	suggested_price_per_kg: float
	low: float
	high: float
	source: str