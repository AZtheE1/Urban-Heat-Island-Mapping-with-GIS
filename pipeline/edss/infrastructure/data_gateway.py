"""Infrastructure gateway for loading regional environmental data."""

import json
import os

import pandas as pd

from pipeline.heat_risk import (
    LST_COLUMNS,
    NDVI_COLUMNS,
    _extract_numeric_series,
    compute_heat_risk_from_dataframe,
)
from pipeline.climate_resilience import compute_climate_resilience_from_dataframe
from pipeline.recommendations import generate_recommendations_from_dataframe

from ..domain.constants import SUPPORTED_REGIONS


def _numeric_summary(series):
    clean = series.dropna()
    if clean.empty:
        return None
    return {
        "min": round(float(clean.min()), 4),
        "max": round(float(clean.max()), 4),
        "mean": round(float(clean.mean()), 4),
        "median": round(float(clean.median()), 4),
        "count": int(len(clean)),
    }


def load_region_metadata(base_dir, region):
    metrics_path = os.path.join(base_dir, "ml_models", f"{region}_reg_metrics.json")
    region_name = region.replace("_", " ").title()
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as handle:
            metrics = json.load(handle)
        region_name = metrics.get("region_name", region_name)
    return {"region": region, "name": region_name}


def load_environmental_snapshot(base_dir, region):
    """
    Load and aggregate LST, NDVI, HRI, climate score, and recommendations
    for a single region from existing pipeline modules.
    """
    if region not in SUPPORTED_REGIONS:
        raise ValueError(
            f"Unsupported region '{region}'. Supported: {', '.join(SUPPORTED_REGIONS)}"
        )

    csv_path = os.path.join(base_dir, "field_data", f"{region}_data_calculated.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Data not pre-computed for region: {region}. Run main.py first."
        )

    df = pd.read_csv(csv_path).reset_index(drop=True)
    metadata = load_region_metadata(base_dir, region)

    lst = _extract_numeric_series(df, LST_COLUMNS)
    ndvi = _extract_numeric_series(df, NDVI_COLUMNS)
    heat_records = compute_heat_risk_from_dataframe(df)
    climate = compute_climate_resilience_from_dataframe(df)
    recommendations, recommendation_summary = generate_recommendations_from_dataframe(df)

    built_up_surfaces = {"Asphalt", "Concrete", "Bare Soil"}
    built_up_count = 0
    if "SurfaceType" in df.columns:
        built_up_count = int(df["SurfaceType"].isin(built_up_surfaces).sum())

    heat_values = [record["heatRiskIndex"] for record in heat_records]
    heat_risk_distribution = {}
    for record in heat_records:
        level = record["riskLevel"]
        heat_risk_distribution[level] = heat_risk_distribution.get(level, 0) + 1

    beta_slope = 6.5
    metrics_path = os.path.join(base_dir, "ml_models", f"{region}_reg_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as handle:
            metrics = json.load(handle)
        beta_slope = float(metrics.get("beta_slope", beta_slope))

    return {
        "region": region,
        "name": metadata["name"],
        "locationCount": len(df),
        "regressionBeta": beta_slope,
        "lst": {
            "unit": "C",
            **_numeric_summary(lst),
        },
        "ndvi": _numeric_summary(ndvi),
        "heatRiskIndex": {
            "average": round(sum(heat_values) / len(heat_values), 4) if heat_values else 0.0,
            "max": round(max(heat_values), 4) if heat_values else 0.0,
            "min": round(min(heat_values), 4) if heat_values else 0.0,
            "distribution": heat_risk_distribution,
            "topHotspots": sorted(heat_records, key=lambda item: item["heatRiskIndex"], reverse=True)[:5],
        },
        "climateScore": {
            "score": climate["climateResilienceScore"],
            "category": climate["category"],
            "summary": climate["summary"],
            "breakdown": climate["breakdown"],
        },
        "recommendations": {
            "summary": recommendation_summary,
            "priorityItems": [item for item in recommendations if item.get("priorityArea")][:10],
            "topItems": recommendations[:10],
        },
        "surfaceProfile": {
            "builtUpLocations": built_up_count,
            "builtUpPercentage": round((built_up_count / len(df)) * 100, 2) if len(df) else 0.0,
        },
    }
