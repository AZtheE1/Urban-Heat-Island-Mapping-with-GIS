"""Climate resilience scoring engine."""

import numpy as np
import pandas as pd

from pipeline.heat_risk import (
    LST_COLUMNS,
    NDVI_COLUMNS,
    LAT_COLUMNS,
    LNG_COLUMNS,
    _extract_numeric_series,
    _first_present_column,
    classify_risk_level,
    compute_heat_risk_from_dataframe,
    min_max_normalize,
    LST_MAX,
    LST_MIN,
    NDVI_MAX,
    NDVI_MIN,
)

from .categories import classify_resilience_category
from .explanation import build_score_explanation
from .green_coverage import compute_regional_green_coverage, estimate_location_green_coverage
from .scoring import build_component_breakdown

NAME_COLUMNS = ("LocationName", "locationName", "name")


def _compute_location_hri(lst_value, ndvi_value):
    norm_lst = float(min_max_normalize(np.array([lst_value]), LST_MIN, LST_MAX)[0])
    norm_ndvi = float(min_max_normalize(np.array([ndvi_value]), NDVI_MIN, NDVI_MAX)[0])
    return round(norm_lst * (1.0 - norm_ndvi), 4)


def _build_location_records(df, lst, ndvi, lat, lng, name_col):
    records = []
    for idx in df.index:
        if pd.isna(lat.iloc[idx]) or pd.isna(lng.iloc[idx]):
            continue
        if pd.isna(lst.iloc[idx]) or pd.isna(ndvi.iloc[idx]):
            continue

        lst_value = float(lst.iloc[idx])
        ndvi_value = float(ndvi.iloc[idx])
        hri_value = _compute_location_hri(lst_value, ndvi_value)
        surface_type = df.loc[idx, "SurfaceType"] if "SurfaceType" in df.columns else None
        green_pct = estimate_location_green_coverage(surface_type, ndvi_value)

        location_score, location_breakdown = build_component_breakdown(
            ndvi_value,
            lst_value,
            hri_value,
            green_pct,
        )

        location_name = None
        if name_col is not None and pd.notna(df.loc[idx, name_col]):
            location_name = str(df.loc[idx, name_col])

        records.append(
            {
                "locationName": location_name,
                "lat": round(float(lat.iloc[idx]), 6),
                "lng": round(float(lng.iloc[idx]), 6),
                "climateResilienceScore": location_score,
                "category": classify_resilience_category(location_score),
                "metrics": {
                    "ndvi": round(ndvi_value, 4),
                    "averageTemperature": round(lst_value, 4),
                    "heatRiskIndex": hri_value,
                    "greenCoveragePercentage": green_pct,
                    "heatRiskLevel": classify_risk_level(hri_value),
                },
                "breakdown": location_breakdown,
            }
        )

    records.sort(key=lambda item: item["climateResilienceScore"], reverse=True)
    return records


def compute_climate_resilience_from_dataframe(df):
    """
    Calculate regional and per-location climate resilience scores (0-100).

    Composite score uses equally weighted contributions from NDVI, average
    temperature, heat risk index, and green coverage percentage.
    """
    if df.empty:
        raise ValueError("Regional dataset is empty.")

    lat_col = _first_present_column(df, LAT_COLUMNS)
    lng_col = _first_present_column(df, LNG_COLUMNS)
    name_col = _first_present_column(df, NAME_COLUMNS)

    if lat_col is None or lng_col is None:
        raise ValueError("Latitude and Longitude columns are required.")

    lst = _extract_numeric_series(df, LST_COLUMNS)
    ndvi = _extract_numeric_series(df, NDVI_COLUMNS)
    lat = pd.to_numeric(df[lat_col], errors="coerce")
    lng = pd.to_numeric(df[lng_col], errors="coerce")

    valid_mask = lat.notna() & lng.notna() & lst.notna() & ndvi.notna()
    if not valid_mask.any():
        raise ValueError("No valid temperature and NDVI records found.")

    avg_ndvi = float(ndvi[valid_mask].mean())
    avg_temperature = float(lst[valid_mask].mean())
    green_coverage_percentage = compute_regional_green_coverage(df[valid_mask], ndvi[valid_mask])

    heat_risk_records = compute_heat_risk_from_dataframe(df[valid_mask])
    avg_heat_risk_index = (
        sum(record["heatRiskIndex"] for record in heat_risk_records) / len(heat_risk_records)
        if heat_risk_records
        else 0.0
    )

    climate_score, breakdown = build_component_breakdown(
        avg_ndvi,
        avg_temperature,
        avg_heat_risk_index,
        green_coverage_percentage,
    )
    category = classify_resilience_category(climate_score)
    explanation = build_score_explanation(category, climate_score, breakdown)
    records = _build_location_records(
        df[valid_mask],
        lst[valid_mask],
        ndvi[valid_mask],
        lat[valid_mask],
        lng[valid_mask],
        name_col,
    )

    return {
        "climateResilienceScore": climate_score,
        "category": category,
        "summary": {
            "avgNdvi": round(avg_ndvi, 4),
            "avgTemperature": round(avg_temperature, 4),
            "avgHeatRiskIndex": round(avg_heat_risk_index, 4),
            "greenCoveragePercentage": green_coverage_percentage,
            "locationCount": len(records),
        },
        "breakdown": breakdown,
        "explanation": explanation,
        "records": records,
    }
