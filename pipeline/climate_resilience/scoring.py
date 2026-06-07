"""Component scoring for climate resilience."""

import numpy as np

from pipeline.heat_risk import (
    LST_MAX,
    LST_MIN,
    NDVI_MAX,
    NDVI_MIN,
    min_max_normalize,
)

from .categories import COMPONENT_WEIGHTS


def ndvi_component_score(avg_ndvi):
    """Higher vegetation index improves resilience."""
    normalized = float(min_max_normalize(np.array([avg_ndvi]), NDVI_MIN, NDVI_MAX)[0])
    component_score = normalized * 100.0
    return round(component_score, 2)


def temperature_component_score(avg_temperature):
    """Lower average surface temperature improves resilience."""
    normalized = float(min_max_normalize(np.array([avg_temperature]), LST_MIN, LST_MAX)[0])
    component_score = (1.0 - normalized) * 100.0
    return round(component_score, 2)


def heat_risk_component_score(avg_heat_risk_index):
    """Lower heat risk index improves resilience."""
    bounded_hri = max(0.0, min(1.0, float(avg_heat_risk_index)))
    component_score = (1.0 - bounded_hri) * 100.0
    return round(component_score, 2)


def green_coverage_component_score(green_coverage_percentage):
    """Higher green coverage improves resilience."""
    bounded = max(0.0, min(100.0, float(green_coverage_percentage)))
    return round(bounded, 2)


def build_component_breakdown(
    avg_ndvi,
    avg_temperature,
    avg_heat_risk_index,
    green_coverage_percentage,
):
    """Compute weighted component contributions for the composite score."""
    components = {
        "ndvi": {
            "value": round(float(avg_ndvi), 4),
            "componentScore": ndvi_component_score(avg_ndvi),
        },
        "averageTemperature": {
            "value": round(float(avg_temperature), 4),
            "componentScore": temperature_component_score(avg_temperature),
        },
        "heatRiskIndex": {
            "value": round(float(avg_heat_risk_index), 4),
            "componentScore": heat_risk_component_score(avg_heat_risk_index),
        },
        "greenCoveragePercentage": {
            "value": round(float(green_coverage_percentage), 2),
            "componentScore": green_coverage_component_score(green_coverage_percentage),
        },
    }

    for key, payload in components.items():
        weight = COMPONENT_WEIGHTS[key]
        payload["weight"] = weight
        payload["weightedContribution"] = round(payload["componentScore"] * weight, 2)

    climate_score = round(
        sum(item["weightedContribution"] for item in components.values()),
        2,
    )
    return climate_score, components
