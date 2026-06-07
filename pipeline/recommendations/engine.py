"""Tree plantation and green-infrastructure recommendation engine."""

import pandas as pd

from pipeline.heat_risk import (
    LST_COLUMNS,
    NDVI_COLUMNS,
    LAT_COLUMNS,
    LNG_COLUMNS,
    _extract_numeric_series,
    _first_present_column,
)

from .actions import suggest_actions
from .intervention import classify_intervention_level
from .scoring import (
    compute_vegetation_deficit_score,
    is_priority_area,
    regional_min_max_normalize,
)

NAME_COLUMNS = ("LocationName", "locationName", "name")


def generate_recommendations_from_dataframe(df):
    """
    Analyze regional LST/NDVI records and produce plantation recommendations.

    Identifies high-temperature, low-NDVI priority areas, estimates vegetation
    deficit scores, and assigns intervention tiers with suggested actions.
    """
    if df.empty:
        return [], {}

    lat_col = _first_present_column(df, LAT_COLUMNS)
    lng_col = _first_present_column(df, LNG_COLUMNS)
    name_col = _first_present_column(df, NAME_COLUMNS)

    if lat_col is None or lng_col is None:
        raise ValueError("Latitude and Longitude columns are required.")

    lst = _extract_numeric_series(df, LST_COLUMNS)
    ndvi = _extract_numeric_series(df, NDVI_COLUMNS)
    lat = pd.to_numeric(df[lat_col], errors="coerce")
    lng = pd.to_numeric(df[lng_col], errors="coerce")

    norm_lst = regional_min_max_normalize(lst)
    norm_ndvi = regional_min_max_normalize(ndvi)

    regional_lst_mean = float(lst.mean())
    regional_ndvi_mean = float(ndvi.mean())

    recommendations = []
    for idx in df.index:
        if pd.isna(lat.iloc[idx]) or pd.isna(lng.iloc[idx]):
            continue
        if pd.isna(lst.iloc[idx]) or pd.isna(ndvi.iloc[idx]):
            continue

        lst_value = float(lst.iloc[idx])
        ndvi_value = float(ndvi.iloc[idx])
        deficit_score = compute_vegetation_deficit_score(norm_lst[idx], norm_ndvi[idx])
        intervention_level = classify_intervention_level(deficit_score)
        surface_type = df.loc[idx, "SurfaceType"] if "SurfaceType" in df.columns else None
        traffic_density = (
            df.loc[idx, "TrafficDensity"] if "TrafficDensity" in df.columns else None
        )

        location_name = None
        if name_col is not None and pd.notna(df.loc[idx, name_col]):
            location_name = str(df.loc[idx, name_col])

        recommendations.append(
            {
                "locationName": location_name,
                "lat": round(float(lat.iloc[idx]), 6),
                "lng": round(float(lng.iloc[idx]), 6),
                "lst": round(lst_value, 4),
                "ndvi": round(ndvi_value, 4),
                "surfaceType": surface_type,
                "vegetationDeficitScore": round(deficit_score, 4),
                "priorityArea": is_priority_area(
                    lst_value,
                    ndvi_value,
                    deficit_score,
                    regional_lst_mean,
                    regional_ndvi_mean,
                ),
                "interventionLevel": intervention_level,
                "suggestedActions": suggest_actions(
                    intervention_level,
                    surface_type=surface_type,
                    traffic_density=traffic_density,
                ),
            }
        )

    recommendations.sort(key=lambda item: item["vegetationDeficitScore"], reverse=True)

    priority_count = sum(1 for item in recommendations if item["priorityArea"])
    avg_deficit = (
        round(
            sum(item["vegetationDeficitScore"] for item in recommendations)
            / len(recommendations),
            4,
        )
        if recommendations
        else 0.0
    )

    summary = {
        "totalLocations": len(recommendations),
        "priorityAreas": priority_count,
        "avgVegetationDeficitScore": avg_deficit,
    }
    return recommendations, summary
