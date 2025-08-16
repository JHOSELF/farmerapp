from __future__ import annotations

from typing import Tuple

import numpy as np

# NOTE: This is a placeholder. Replace with a real model (e.g., a fine-tuned CNN) later.

KNOWN_DISEASES = {
	"leaf_blight": {
		"advice": [
			"Remove infected leaves to reduce spread.",
			"Apply copper-based fungicide following label rates.",
			"Avoid overhead irrigation; water at soil level.",
		],
	},
	"powdery_mildew": {
		"advice": [
			"Improve airflow; prune dense canopies.",
			"Apply sulfur or potassium bicarbonate early.",
			"Avoid excess nitrogen fertilization.",
		],
	},
	"rust": {
		"advice": [
			"Rotate crops and remove volunteer plants.",
			"Use resistant varieties if available.",
			"Timely fungicide application at first sign.",
		],
	},
	"healthy": {
		"advice": [
			"No visible disease. Maintain balanced fertilization.",
			"Scout weekly and monitor moisture stress.",
			"Keep foliage dry and ensure good spacing.",
		],
	},
}


def predict_disease(image_array: np.ndarray) -> Tuple[str, float, list[str]]:
	if image_array.ndim != 3 or image_array.shape[2] != 3:
		return "unknown", 0.0, ["Unrecognized image format"]

	# Simple heuristic: Examine color statistics
	mean_channels = image_array.mean(axis=(0, 1))  # R, G, B
	red_mean, green_mean, blue_mean = mean_channels.tolist()

	# Heuristic rules
	if green_mean > red_mean + 15 and green_mean > blue_mean + 15:
		label = "healthy"
		confidence = 0.6
	elif red_mean > green_mean + 10:
		label = "rust"
		confidence = 0.55
	elif blue_mean > green_mean + 10:
		label = "powdery_mildew"
		confidence = 0.5
	else:
		label = "leaf_blight"
		confidence = 0.5

	advice = KNOWN_DISEASES.get(label, KNOWN_DISEASES["healthy"]) ["advice"]
	return label, float(round(confidence, 2)), advice