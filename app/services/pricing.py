from __future__ import annotations

from typing import Tuple

# Placeholder price data; in reality, fetch from market APIs or datasets
BASE_PRICES = {
	"maize": 0.22,  # USD/kg
	"rice": 0.45,
	"wheat": 0.30,
	"tomato": 0.50,
	"potato": 0.25,
}

REGION_ADJUSTMENTS = {
	"default": 1.0,
	"lagos": 1.15,
	"nairobi": 1.10,
	"delhi": 0.95,
}


def suggest_price(crop_name: str, location: str | None) -> Tuple[float, float, float, str]:
	crop_key = crop_name.lower().strip()
	base = BASE_PRICES.get(crop_key, 0.35)
	factor = REGION_ADJUSTMENTS.get((location or "").lower(), REGION_ADJUSTMENTS["default"])
	price = base * factor
	low = price * 0.9
	high = price * 1.1
	return round(price, 2), round(low, 2), round(high, 2), "heuristic"