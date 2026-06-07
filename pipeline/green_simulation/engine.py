"""Green infrastructure growth simulation engine."""

import os

import pandas as pd

from pipeline.heat_risk import (
    LST_COLUMNS,
    NDVI_COLUMNS,
    LAT_COLUMNS,
    LNG_COLUMNS,
    _extract_numeric_series,
    _first_present_column,
)

from pipeline.climate_resilience.green_coverage import compute_regional_green_coverage

from .constants import DEFAULT_VEGETATION_SCENARIOS, NDVI_MAX, NDVI_MIN
from .intervention import compute_intervention_impact
from .regression import estimate_temperature, load_regression_coefficients

NAME_COLUMNS = ("LocationName", "locationName", "name")


def _clip_ndvi(ndvi):
    return max(NDVI_MIN, min(NDVI_MAX, float(ndvi)))


def _apply_vegetation_increase(current_ndvi, increase_percent):
    """Increase NDVI by a percentage of its current value, capped at NDVI_MAX."""
    increased = float(current_ndvi) * (1.0 + float(increase_percent) / 100.0)
    return round(_clip_ndvi(increased), 4)


def _build_scenario(current_temperature, current_ndvi, increase_percent, alpha, beta):
    simulated_ndvi = _apply_vegetation_increase(current_ndvi, increase_percent)
    estimated_temperature = round(estimate_temperature(alpha, beta, simulated_ndvi), 4)
    reduction = round(float(current_temperature) - estimated_temperature, 4)

    return {
        "vegetationIncreasePercent": int(increase_percent),
        "currentTemperature": round(float(current_temperature), 4),
        "currentNDVI": round(float(current_ndvi), 4),
        "simulatedNDVI": simulated_ndvi,
        "estimatedTemperature": estimated_temperature,
        "reduction": reduction,
    }


def _resolve_point_baseline(df, lat=None, lng=None):
    lat_col = _first_present_column(df, LAT_COLUMNS)
    lng_col = _first_present_column(df, LNG_COLUMNS)
    if lat is None or lng is None:
        return None

    if lat_col is None or lng_col is None:
        raise ValueError("Regional dataset does not include coordinates for point simulation.")

    target_lat = float(lat)
    target_lng = float(lng)
    lat_series = pd.to_numeric(df[lat_col], errors="coerce")
    lng_series = pd.to_numeric(df[lng_col], errors="coerce")
    distances = ((lat_series - target_lat) ** 2 + (lng_series - target_lng) ** 2).pow(0.5)
    nearest_idx = distances.idxmin()

    lst = _extract_numeric_series(df, LST_COLUMNS)
    ndvi = _extract_numeric_series(df, NDVI_COLUMNS)
    name_col = _first_present_column(df, NAME_COLUMNS)

    location_name = None
    if name_col and pd.notna(df.loc[nearest_idx, name_col]):
        location_name = str(df.loc[nearest_idx, name_col])

    return {
        "locationName": location_name,
        "lat": round(float(lat_series.loc[nearest_idx]), 6),
        "lng": round(float(lng_series.loc[nearest_idx]), 6),
        "currentTemperature": round(float(lst.loc[nearest_idx]), 4),
        "currentNDVI": round(float(ndvi.loc[nearest_idx]), 4),
    }


def _resolve_regional_baseline(df, coefficients):
    lst = _extract_numeric_series(df, LST_COLUMNS)
    ndvi = _extract_numeric_series(df, NDVI_COLUMNS)
    return {
        "locationName": None,
        "lat": None,
        "lng": None,
        "currentTemperature": round(float(lst.mean()), 4),
        "currentNDVI": round(float(ndvi.mean()), 4),
    }


def simulate_green_growth(
    base_dir,
    region,
    scenarios=None,
    lat=None,
    lng=None,
    custom_increase=None,
):
    """
    Simulate temperature reduction from hypothetical vegetation (NDVI) increases.

    Uses the regional linear regression model:
      Temperature = alpha - (beta * NDVI)
    """
    csv_path = os.path.join(base_dir, "field_data", f"{region}_data_calculated.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Data not pre-computed for region: {region}. Run main.py first."
        )

    coefficients = load_regression_coefficients(base_dir, region)
    df = pd.read_csv(csv_path).reset_index(drop=True)

    baseline = _resolve_point_baseline(df, lat=lat, lng=lng)
    if baseline is None:
        baseline = _resolve_regional_baseline(df, coefficients)

    selected_scenarios = list(scenarios or DEFAULT_VEGETATION_SCENARIOS)
    if custom_increase is not None:
        selected_scenarios.append(int(custom_increase))
    selected_scenarios = sorted(set(int(value) for value in selected_scenarios if int(value) > 0))

    if not selected_scenarios:
        raise ValueError("At least one positive vegetation increase scenario is required.")

    alpha = coefficients["alpha"]
    beta = coefficients["beta"]
    scenario_results = [
        _build_scenario(
            baseline["currentTemperature"],
            baseline["currentNDVI"],
            increase_percent,
            alpha,
            beta,
        )
        for increase_percent in selected_scenarios
    ]

    return {
        "region": region,
        "name": coefficients["regionName"],
        "model": "linear_regression",
        "formula": coefficients["formula"],
        "regressionMetrics": {
            "r2Score": coefficients.get("r2Score"),
            "rmse": coefficients.get("rmse"),
        },
        "baseline": baseline,
        "scenarios": scenario_results,
    }


def simulate_green_infrastructure(
    base_dir,
    region,
    vegetation_increase_percent=0,
    tree_plantation_count=0,
    green_roof_coverage=0,
    lat=None,
    lng=None,
):
    """
    Run a composite green infrastructure planning simulation with real-time
    intervention parameters and before/after climate impact estimates.
    """
    csv_path = os.path.join(base_dir, "field_data", f"{region}_data_calculated.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Data not pre-computed for region: {region}. Run main.py first."
        )

    coefficients = load_regression_coefficients(base_dir, region)
    df = pd.read_csv(csv_path).reset_index(drop=True)
    ndvi = _extract_numeric_series(df, NDVI_COLUMNS)

    baseline = _resolve_point_baseline(df, lat=lat, lng=lng)
    if baseline is None:
        baseline = _resolve_regional_baseline(df, coefficients)

    green_coverage = compute_regional_green_coverage(df, ndvi)
    location_count = max(len(df), 1)

    impact = compute_intervention_impact(
        baseline_temperature=baseline["currentTemperature"],
        baseline_ndvi=baseline["currentNDVI"],
        baseline_green_coverage=green_coverage,
        alpha=coefficients["alpha"],
        beta=coefficients["beta"],
        vegetation_increase_percent=vegetation_increase_percent,
        tree_plantation_count=tree_plantation_count,
        green_roof_coverage=green_roof_coverage,
        location_count=location_count,
    )

    return {
        "region": region,
        "name": coefficients["regionName"],
        "model": "linear_regression",
        "formula": coefficients["formula"],
        "coefficients": {
            "alpha": coefficients["alpha"],
            "beta": coefficients["beta"],
        },
        "regressionMetrics": {
            "r2Score": coefficients.get("r2Score"),
            "rmse": coefficients.get("rmse"),
        },
        "baseline": baseline,
        "locationCount": location_count,
        **impact,
    }
