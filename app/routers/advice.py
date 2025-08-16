from __future__ import annotations

from fastapi import APIRouter

from ..schemas.advice import AdviceRequest, AdviceResponse
from ..services.advice_engine import generate_advice

router = APIRouter()


@router.post("/recommend", response_model=AdviceResponse)
def recommend_advice(request: AdviceRequest) -> AdviceResponse:
	recommendations, schedules, alerts = generate_advice(request)
	return AdviceResponse(
		crop_name=request.crop_name,
		growth_stage=request.growth_stage,
		recommendations=recommendations,
		schedules=schedules,
		alerts=alerts,
	)