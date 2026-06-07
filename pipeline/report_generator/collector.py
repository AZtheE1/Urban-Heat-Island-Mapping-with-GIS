"""Collect environmental analytics for report generation."""

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

from .constants import SUPPORTED_REGIONS


def _numeric_statistics(series):
    clean = series.dropna()
    if clean.empty:
        return None
    return {
        "min": round(float(clean.min()), 4),
        "max": round(float(clean.max()), 4),
        "mean": round(float(clean.mean()), 4),
        "median": round(float(clean.median()), 4),
        "std": round(float(clean.std(ddof=0)), 4),
        "count": int(len(clean)),
    }


def _heat_risk_summary(heat_records):
    if not heat_records:
        return None

    values = [record["heatRiskIndex"] for record in heat_records]
    distribution = {}
    for record in heat_records:
        level = record["riskLevel"]
        distribution[level] = distribution.get(level, 0) + 1

    sorted_records = sorted(heat_records, key=lambda item: item["heatRiskIndex"], reverse=True)
    return {
        "average": round(sum(values) / len(values), 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "riskLevelDistribution": distribution,
        "topHotspots": sorted_records[:5],
    }


def load_region_metadata(base_dir, region):
    metrics_path = os.path.join(base_dir, "ml_models", f"{region}_reg_metrics.json")
    region_name = region.replace("_", " ").title()
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as handle:
            metrics = json.load(handle)
        region_name = metrics.get("region_name", region_name)
    return {"region": region, "name": region_name}


def collect_region_report(base_dir, region, regional_descriptions=None):
    """Aggregate all report sections for a single region."""
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

    description = None
    if regional_descriptions:
        description = regional_descriptions.get(region)

    return {
        "region": region,
        "name": metadata["name"],
        "description": description,
        "locationCount": len(df),
        "temperatureStatistics": _numeric_statistics(lst),
        "ndviStatistics": _numeric_statistics(ndvi),
        "heatRiskIndex": _heat_risk_summary(heat_records),
        "climateScore": {
            "score": climate["climateResilienceScore"],
            "category": climate["category"],
            "summary": climate["summary"],
            "breakdown": climate["breakdown"],
            "explanation": climate["explanation"],
        },
        "recommendations": {
            "summary": recommendation_summary,
            "items": recommendations[:10],
        },
    }


def collect_multi_region_report(base_dir, regions, regional_descriptions=None):
    """Collect report sections for one or more selected regions."""
    if not regions:
        raise ValueError("At least one region must be selected.")

    sections = []
    for region in regions:
        sections.append(collect_region_report(base_dir, region, regional_descriptions))

    return sections
