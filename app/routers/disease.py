from __future__ import annotations

from io import BytesIO
from typing import Optional

import numpy as np
from fastapi import APIRouter, File, UploadFile, HTTPException
from PIL import Image

from ..services.disease_model import predict_disease

router = APIRouter()


@router.post("/identify")
async def identify_disease(image: UploadFile = File(...)) -> dict:
	if image.content_type not in {"image/jpeg", "image/png"}:
		raise HTTPException(status_code=400, detail="Only JPEG or PNG images are supported")

	image_bytes = await image.read()
	if len(image_bytes) == 0:
		raise HTTPException(status_code=400, detail="Empty image")

	try:
		pil_image = Image.open(BytesIO(image_bytes)).convert("RGB")
	except Exception as exc:
		raise HTTPException(status_code=400, detail=f"Invalid image: {exc}")

	image_array = np.array(pil_image)

	label, confidence, tips = predict_disease(image_array)
	return {
		"disease": label,
		"confidence": confidence,
		"advice": tips,
	}