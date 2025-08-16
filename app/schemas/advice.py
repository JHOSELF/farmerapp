from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class AdviceRequest(BaseModel):
	crop_name: str = Field(..., description="Crop name, e.g., 'maize', 'rice', 'wheat'")
	growth_stage: str = Field(..., description="Stage: pre-planting, vegetative, flowering, fruiting, harvest")
	soil_type: Optional[str] = Field(None, description="sandy, loam, clay")
	soil_ph: Optional[float] = Field(None, ge=0, le=14)
	rainfall_mm_last_7d: Optional[float] = Field(None, ge=0)
	temperature_c: Optional[float] = Field(None)
	irrigation_available: Optional[bool] = Field(None)
	location: Optional[str] = Field(None, description="Region or district name")
	farm_size_ha: Optional[float] = Field(None, ge=0)

	@field_validator("growth_stage")
	@classmethod
	def validate_stage(cls, value: str) -> str:
		allowed = {"pre-planting", "vegetative", "flowering", "fruiting", "harvest"}
		if value not in allowed:
			raise ValueError(f"growth_stage must be one of {sorted(allowed)}")
		return value


class AdviceResponse(BaseModel):
	crop_name: str
	growth_stage: str
	recommendations: List[str]
	schedules: dict
	alerts: List[str]