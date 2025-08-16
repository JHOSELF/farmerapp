from __future__ import annotations

from typing import List, Dict

from ..schemas.advice import AdviceRequest


def generate_advice(request: AdviceRequest) -> tuple[list[str], dict, list[str]]:
	recommendations: List[str] = []
	schedules: Dict[str, str] = {}
	alerts: List[str] = []

	crop = request.crop_name.lower().strip()
	stage = request.growth_stage
	soil_ph = request.soil_ph
	soil_type = (request.soil_type or "").lower()
	rain_last_week = request.rainfall_mm_last_7d or 0.0
	temp_c = request.temperature_c
	irrigation = bool(request.irrigation_available)

	# Soil pH recommendations
	if soil_ph is not None:
		if soil_ph < 5.5:
			recommendations.append("Soil is acidic. Incorporate agricultural lime (1-2 t/ha) and recheck pH in 4-6 weeks.")
		elif soil_ph > 7.5:
			recommendations.append("Soil is alkaline. Add elemental sulfur/acidifying fertilizers and organic matter.")
		else:
			recommendations.append("Soil pH is within an acceptable range for most crops.")
	else:
		recommendations.append("Test soil pH to optimize nutrient availability.")

	# Soil type recommendations
	if soil_type:
		if soil_type == "sandy":
			recommendations.append("Sandy soil: apply smaller, more frequent irrigations and add organic matter to improve water holding.")
		elif soil_type == "clay":
			recommendations.append("Clay soil: improve drainage with raised beds and avoid working soil when wet.")
		elif soil_type == "loam":
			recommendations.append("Loam: balanced texture, maintain organic inputs.")
		else:
			recommendations.append("Unknown soil type: incorporate compost to improve structure.")

	# Stage-based guidance
	if stage == "pre-planting":
		recommendations.extend([
			"Use certified seeds and treat seeds if disease risk is high.",
			"Prepare a fine seedbed and ensure proper field leveling.",
		])
		schedules["planting_density"] = _planting_density(crop)
	elif stage == "vegetative":
		recommendations.extend([
			"Top-dress nitrogen based on crop requirement.",
			"Scout weekly for pests and weeds; control early.",
		])
		schedules["fertilizer"] = _fertilizer_schedule(crop)
	elif stage in {"flowering", "fruiting"}:
		recommendations.extend([
			"Avoid stress during flowering; maintain even soil moisture.",
			"Apply potassium as per recommendations to improve yield quality.",
		])
		schedules["irrigation"] = _irrigation_schedule(crop, rain_last_week, irrigation)
	elif stage == "harvest":
		recommendations.extend([
			"Harvest at physiological maturity and avoid mechanical damage.",
			"Dry produce to safe moisture levels and store in clean, ventilated storage.",
		])
		schedules["harvest"] = _harvest_guidance(crop)

	# Weather-based alerts
	if temp_c is not None:
		if temp_c >= 35:
			alerts.append("High temperature: risk of heat stress; irrigate in early morning or late evening.")
		elif temp_c <= 10:
			alerts.append("Low temperature: protect seedlings from cold snaps.")

	if rain_last_week >= 80:
		alerts.append("High rainfall: increased risk of fungal diseases; ensure drainage and consider preventive fungicide.")
	elif rain_last_week <= 5:
		alerts.append("Low rainfall: monitor soil moisture closely; mulching can reduce evaporation.")

	return recommendations, schedules, alerts


def _planting_density(crop: str) -> str:
	if crop in {"maize", "corn"}:
		return "Maize: 60-75 cm row spacing, 20-25 cm plant spacing (~53-83k plants/ha)."
	if crop == "rice":
		return "Rice: transplant 2-3 seedlings/hill at 20x20 cm or direct seed at 80-100 kg/ha."
	if crop == "wheat":
		return "Wheat: drill at 18-22 cm rows, 100-125 kg seed/ha."
	return "Use local recommendations for spacing and seed rate."


def _fertilizer_schedule(crop: str) -> str:
	if crop in {"maize", "corn"}:
		return "Maize: Split N applications (e.g., 30% at planting, 40% at V6, 30% at V10); apply P & K at planting."
	if crop == "rice":
		return "Rice: Apply N in 3 splits (basal, tillering, panicle initiation); P & K as basal."
	if crop == "wheat":
		return "Wheat: 50% N at sowing, 50% at crown root initiation; P & K as basal."
	return "Follow soil test-based fertilizer recommendations."


def _irrigation_schedule(crop: str, rain_last_week: float, irrigation: bool) -> str:
	if not irrigation:
		return "No irrigation available: prioritize mulching and conserve soil moisture."
	if crop in {"maize", "corn"}:
		need = 35
	elif crop == "rice":
		need = 50
	elif crop == "wheat":
		need = 30
	else:
		need = 25
	deficit = max(0.0, need - rain_last_week)
	return f"Apply ~{int(deficit)} mm this week split into 2-3 irrigations; avoid waterlogging."


def _harvest_guidance(crop: str) -> str:
	if crop in {"maize", "corn"}:
		return "Harvest when husks dry and kernels dent; dry to ~13-14% moisture."
	if crop == "rice":
		return "Harvest 20-25 days after flowering when grains are hard; dry to ~12-14% moisture." 
	if crop == "wheat":
		return "Harvest at full maturity; dry to ~12% moisture."
	return "Harvest at physiological maturity; handle gently to reduce losses."