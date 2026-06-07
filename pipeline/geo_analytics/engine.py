"""GeoJSON polygon analytics engine."""

import pandas as pd

from pipeline.heat_risk import (
    _extract_numeric_series,
    _first_present_column,
    classify_risk_level,
    compute_heat_risk_from_dataframe,
    LAT_COLUMNS,
    LNG_COLUMNS,
    LST_COLUMNS,
    NDVI_COLUMNS,
)

from .adapters.geojson_adapter import GeoJSONAdapter
from .spatial import (
    approximate_polygon_area_sq_km,
    compute_bounding_box,
    point_in_any_polygon,
)


def _filter_points_in_polygons(df, rings):
    lat_col = _first_present_column(df, LAT_COLUMNS)
    lng_col = _first_present_column(df, LNG_COLUMNS)
    if lat_col is None or lng_col is None:
        raise ValueError("Regional dataset must include Latitude and Longitude columns.")

    lat = pd.to_numeric(df[lat_col], errors="coerce")
    lng = pd.to_numeric(df[lng_col], errors="coerce")
    mask = [
        point_in_any_polygon(float(lng.iloc[idx]), float(lat.iloc[idx]), rings)
        if pd.notna(lat.iloc[idx]) and pd.notna(lng.iloc[idx])
        else False
        for idx in df.index
    ]
    return df[mask].copy().reset_index(drop=True)


def _compute_average_hri(df):
    records = compute_heat_risk_from_dataframe(df)
    if not records:
        return 0.0, "Very Low", []
    avg_hri = sum(item["heatRiskIndex"] for item in records) / len(records)
    return round(avg_hri, 4), classify_risk_level(avg_hri), records


def analyze_region_polygon(base_dir, region, geojson_document, df):
    """
    Analyze environmental statistics for observation points inside a GeoJSON polygon.

    Returns average temperature, average NDVI, average Heat Risk Index, and
    polygon area statistics.
    """
    adapter = GeoJSONAdapter(geojson_document)
    rings = adapter.get_polygon_rings()
    metadata = adapter.get_metadata()

    filtered_df = _filter_points_in_polygons(df, rings)
    total_points = len(df)
    matched_points = len(filtered_df)

    bounding_box = compute_bounding_box(rings)
    approximate_area_sq_km = round(
        sum(approximate_polygon_area_sq_km(ring) for ring in rings),
        4,
    )

    if matched_points == 0:
        return {
            "region": region,
            "geojsonValidation": metadata["validation"],
            "areaStatistics": {
                "pointCount": 0,
                "totalRegionalPoints": total_points,
                "coveragePercentage": 0.0,
                "averageTemperature": None,
                "averageNdvi": None,
                "averageHeatRiskIndex": None,
                "heatRiskLevel": None,
                "boundingBox": bounding_box,
                "approximateAreaSqKm": approximate_area_sq_km,
                "polygonCount": len(rings),
            },
            "points": [],
            "message": "No regional observation points fall inside the uploaded polygon.",
        }

    lst = _extract_numeric_series(filtered_df, LST_COLUMNS)
    ndvi = _extract_numeric_series(filtered_df, NDVI_COLUMNS)
    avg_temperature = round(float(lst.mean()), 4)
    avg_ndvi = round(float(ndvi.mean()), 4)
    avg_hri, heat_risk_level, point_records = _compute_average_hri(filtered_df)

    coverage_percentage = round((matched_points / total_points) * 100.0, 2) if total_points else 0.0

    return {
        "region": region,
        "geojsonValidation": metadata["validation"],
        "areaStatistics": {
            "pointCount": matched_points,
            "totalRegionalPoints": total_points,
            "coveragePercentage": coverage_percentage,
            "averageTemperature": avg_temperature,
            "averageNdvi": avg_ndvi,
            "averageHeatRiskIndex": avg_hri,
            "heatRiskLevel": heat_risk_level,
            "boundingBox": bounding_box,
            "approximateAreaSqKm": approximate_area_sq_km,
            "polygonCount": len(rings),
        },
        "points": point_records,
    }
