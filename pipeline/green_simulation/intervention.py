"""Composite green infrastructure intervention modeling."""

from pipeline.climate_resilience.categories import classify_resilience_category
from pipeline.climate_resilience.scoring import build_component_breakdown
from pipeline.heat_risk import LST_MIN, LST_MAX, NDVI_MIN, NDVI_MAX, min_max_normalize

from .constants import NDVI_MAX as SIM_NDVI_MAX, NDVI_MIN as SIM_NDVI_MIN
from .regression import estimate_temperature
import numpy as np


def _clip_ndvi(ndvi):
    return max(SIM_NDVI_MIN, min(SIM_NDVI_MAX, float(ndvi)))


def _compute_hri(lst_value, ndvi_value):
    norm_lst = float(min_max_normalize(np.array([lst_value]), LST_MIN, LST_MAX)[0])
    norm_ndvi = float(min_max_normalize(np.array([ndvi_value]), NDVI_MIN, NDVI_MAX)[0])
    return round(norm_lst * (1.0 - norm_ndvi), 4)


def _estimate_green_coverage_boost(green_roof_coverage, tree_count, location_count):
    """Translate planning inputs into an effective green coverage uplift (%)."""
    roof_uplift = float(green_roof_coverage) * 0.35
    tree_uplift = min(25.0, (float(tree_count) / max(location_count, 1)) * 1.2)
    return round(roof_uplift + tree_uplift, 2)


def compute_intervention_impact(
    baseline_temperature,
    baseline_ndvi,
    baseline_green_coverage,
    alpha,
    beta,
    vegetation_increase_percent=0,
    tree_plantation_count=0,
    green_roof_coverage=0,
    location_count=20,
):
    """
    Model combined green infrastructure interventions on NDVI, temperature,
    heat risk, and climate resilience score.
    """
    veg_boost = float(baseline_ndvi) * (float(vegetation_increase_percent) / 100.0)
    tree_boost = min(0.18, float(tree_plantation_count) * 0.00004)
    roof_boost = min(0.14, float(green_roof_coverage) * 0.0012)

    simulated_ndvi = _clip_ndvi(float(baseline_ndvi) + veg_boost + tree_boost + roof_boost)
    simulated_temperature = round(estimate_temperature(alpha, beta, simulated_ndvi), 4)
    temperature_reduction = round(float(baseline_temperature) - simulated_temperature, 4)

    baseline_hri = _compute_hri(baseline_temperature, baseline_ndvi)
    simulated_hri = _compute_hri(simulated_temperature, simulated_ndvi)

    simulated_green_coverage = min(
        100.0,
        float(baseline_green_coverage) + _estimate_green_coverage_boost(
            green_roof_coverage, tree_plantation_count, location_count
        ),
    )

    baseline_score, baseline_breakdown = build_component_breakdown(
        baseline_ndvi,
        baseline_temperature,
        baseline_hri,
        baseline_green_coverage,
    )
    simulated_score, simulated_breakdown = build_component_breakdown(
        simulated_ndvi,
        simulated_temperature,
        simulated_hri,
        simulated_green_coverage,
    )

    return {
        "inputs": {
            "vegetationIncreasePercent": int(vegetation_increase_percent),
            "treePlantationCount": int(tree_plantation_count),
            "greenRoofCoverage": int(green_roof_coverage),
        },
        "before": {
            "temperature": round(float(baseline_temperature), 4),
            "ndvi": round(float(baseline_ndvi), 4),
            "heatRiskIndex": baseline_hri,
            "greenCoverage": round(float(baseline_green_coverage), 2),
            "climateScore": baseline_score,
            "climateCategory": classify_resilience_category(baseline_score),
            "breakdown": baseline_breakdown,
        },
        "after": {
            "temperature": simulated_temperature,
            "ndvi": simulated_ndvi,
            "heatRiskIndex": simulated_hri,
            "greenCoverage": round(simulated_green_coverage, 2),
            "climateScore": simulated_score,
            "climateCategory": classify_resilience_category(simulated_score),
            "breakdown": simulated_breakdown,
        },
        "impact": {
            "temperatureReduction": temperature_reduction,
            "ndviGain": round(simulated_ndvi - float(baseline_ndvi), 4),
            "heatRiskReduction": round(baseline_hri - simulated_hri, 4),
            "climateScoreImprovement": round(simulated_score - baseline_score, 2),
            "greenCoverageGain": round(simulated_green_coverage - float(baseline_green_coverage), 2),
        },
        "interventionBreakdown": {
            "vegetationNdviBoost": round(veg_boost, 4),
            "treeNdviBoost": round(tree_boost, 4),
            "greenRoofNdviBoost": round(roof_boost, 4),
        },
    }
