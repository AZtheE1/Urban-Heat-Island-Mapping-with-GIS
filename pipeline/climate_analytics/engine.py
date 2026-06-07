"""Aggregate comparative and historical climate analytics across regions."""

import json
import os

import numpy as np
import pandas as pd

from pipeline.climate_resilience import compute_climate_resilience_from_dataframe
from pipeline.heat_risk import compute_heat_risk_from_dataframe
from pipeline.heatwave_alerts import evaluate_heatwave_alerts
from pipeline.temperature_prediction.data_loader import load_annual_temperature_series

ANALYTICS_REGIONS = (
    ("dhaka_all", "Dhaka"),
    ("mirpur12", "Mirpur 12"),
    ("sylhet", "Sylhet"),
    ("rajshahi", "Rajshahi"),
    ("chittagong", "Chittagong"),
)

HEATWAVE_THRESHOLD = 35.0


def _load_region_metrics(base_dir, region_id):
    path = os.path.join(base_dir, "ml_models", f"{region_id}_reg_metrics.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _surface_breakdown(df):
    if "SurfaceType" not in df.columns or "Temperature" not in df.columns:
        return []
    grouped = (
        df.groupby("SurfaceType")["Temperature"]
        .agg(["mean", "count"])
        .reset_index()
        .sort_values("mean", ascending=False)
    )
    return [
        {
            "surface": row["SurfaceType"],
            "meanTemp": round(float(row["mean"]), 2),
            "count": int(row["count"]),
        }
        for _, row in grouped.iterrows()
    ]


def _top_hotspots(df, limit=5):
    if df.empty or "Temperature" not in df.columns:
        return []
    name_col = "LocationName" if "LocationName" in df.columns else None
    sorted_df = df.sort_values("Temperature", ascending=False).head(limit)
    hotspots = []
    for _, row in sorted_df.iterrows():
        hotspots.append(
            {
                "name": str(row[name_col]) if name_col and pd.notna(row[name_col]) else "Monitoring point",
                "temperature": round(float(row["Temperature"]), 2),
                "ndvi": round(float(row["NDVI"]), 4) if "NDVI" in row and pd.notna(row["NDVI"]) else None,
                "surface": row.get("SurfaceType"),
                "lat": round(float(row["Latitude"]), 6) if "Latitude" in row and pd.notna(row["Latitude"]) else None,
                "lng": round(float(row["Longitude"]), 6) if "Longitude" in row and pd.notna(row["Longitude"]) else None,
            }
        )
    return hotspots


def _build_region_profile(base_dir, region_id, display_name):
    csv_path = os.path.join(base_dir, "field_data", f"{region_id}_data_calculated.csv")
    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)
    metrics = _load_region_metrics(base_dir, region_id)

    climate = compute_climate_resilience_from_dataframe(df)
    risk_records = compute_heat_risk_from_dataframe(df)
    alerts = evaluate_heatwave_alerts(base_dir, region=region_id, df=df)

    high_risk = sum(1 for r in risk_records if r["riskLevel"] in ("High", "Extreme"))
    avg_hri = (
        round(sum(r["heatRiskIndex"] for r in risk_records) / len(risk_records), 4)
        if risk_records
        else 0.0
    )

    ndvi_col = "NDVI" if "NDVI" in df.columns else "Calculated_NDVI"
    avg_ndvi = round(float(df[ndvi_col].mean()), 4) if ndvi_col in df.columns else None

    return {
        "id": region_id,
        "name": metrics.get("region_name", display_name),
        "shortName": display_name,
        "avgTemp": metrics.get("avg_temp", climate["summary"]["avgTemperature"]),
        "avgNdvi": avg_ndvi or climate["summary"]["avgNdvi"],
        "avgHri": avg_hri,
        "climateScore": climate["climateResilienceScore"],
        "climateCategory": climate["category"],
        "greenCoverage": climate["summary"]["greenCoveragePercentage"],
        "highRiskCount": high_risk,
        "locationCount": climate["summary"]["locationCount"],
        "alertCount": alerts["activeAlertCount"],
        "highestAlertLevel": alerts["highestLevel"],
        "r2Score": metrics.get("r2_score"),
        "rmse": metrics.get("rmse"),
        "peakHotspot": metrics.get("peak_hotspot"),
        "peakCoolspot": metrics.get("peak_coolspot"),
        "surfaceBreakdown": _surface_breakdown(df),
        "hotspots": _top_hotspots(df),
        "riskDistribution": _risk_distribution(risk_records),
        "componentBreakdown": climate["breakdown"],
    }


def _risk_distribution(risk_records):
    counts = {"Very Low": 0, "Low": 0, "Moderate": 0, "High": 0, "Extreme": 0}
    for record in risk_records:
        level = record.get("riskLevel", "Moderate")
        if level in counts:
            counts[level] += 1
    return counts


def _build_historical_trends(base_dir):
    historical_path = os.path.join(base_dir, "field_data", "mirpur_historical_temperatures.csv")
    if not os.path.exists(historical_path):
        return {"annual": [], "monthly": [], "source": None}

    df = pd.read_csv(historical_path, parse_dates=["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["heatwaveDay"] = df["max_temp_C"] > HEATWAVE_THRESHOLD

    annual = (
        df.groupby("year")
        .agg(
            meanTemp=("mean_temp_C", "mean"),
            maxTemp=("max_temp_C", "max"),
            minTemp=("min_temp_C", "min"),
            heatwaveDays=("heatwaveDay", "sum"),
        )
        .reset_index()
        .sort_values("year")
    )

    monthly = (
        df.groupby(["year", "month"])
        .agg(
            meanTemp=("mean_temp_C", "mean"),
            maxTemp=("max_temp_C", "max"),
            heatwaveDays=("heatwaveDay", "sum"),
        )
        .reset_index()
        .sort_values(["year", "month"])
    )

    return {
        "source": "mirpur_historical_temperatures.csv",
        "coverage": "Dhaka metropolitan historical baseline",
        "annual": [
            {
                "year": int(row["year"]),
                "meanTemp": round(float(row["meanTemp"]), 2),
                "maxTemp": round(float(row["maxTemp"]), 2),
                "minTemp": round(float(row["minTemp"]), 2),
                "heatwaveDays": int(row["heatwaveDays"]),
            }
            for _, row in annual.iterrows()
            if row["year"] >= 2020
        ],
        "monthly": [
            {
                "year": int(row["year"]),
                "month": int(row["month"]),
                "label": pd.Timestamp(year=int(row["year"]), month=int(row["month"]), day=1).strftime("%b %Y"),
                "meanTemp": round(float(row["meanTemp"]), 2),
                "maxTemp": round(float(row["maxTemp"]), 2),
                "heatwaveDays": int(row["heatwaveDays"]),
            }
            for _, row in monthly.iterrows()
            if row["year"] >= 2020
        ],
    }


def _build_forecast_snapshot(base_dir):
    try:
        annual, source = load_annual_temperature_series(base_dir)
        if annual.empty:
            return None
        years = annual.index.to_numpy(dtype=int)
        temps = annual.to_numpy(dtype=float)
        slope = float(np.polyfit(years, temps, 1)[0]) if len(years) >= 2 else 0.0
        last_year = int(years[-1])
        last_temp = float(temps[-1])
        return {
            "source": source,
            "lastObservedYear": last_year,
            "lastObservedTemp": round(last_temp, 2),
            "annualTrendCPerYear": round(slope, 4),
            "projected": [
                {"year": last_year + 1, "temp": round(last_temp + slope, 2)},
                {"year": last_year + 3, "temp": round(last_temp + slope * 3, 2)},
                {"year": last_year + 5, "temp": round(last_temp + slope * 5, 2)},
            ],
        }
    except (FileNotFoundError, ValueError):
        return None


def build_climate_analytics(base_dir):
    """Build comparative regional profiles, historical trends, and ranking."""
    regions = []
    for region_id, display_name in ANALYTICS_REGIONS:
        profile = _build_region_profile(base_dir, region_id, display_name)
        if profile:
            regions.append(profile)

    if not regions:
        raise ValueError("No regional analytics profiles could be built.")

    regions.sort(key=lambda item: item["climateScore"], reverse=True)

    historical = _build_historical_trends(base_dir)
    forecast = _build_forecast_snapshot(base_dir)

    comparison = {
        "coolestCity": min(regions, key=lambda r: r["avgTemp"])["shortName"],
        "hottestCity": max(regions, key=lambda r: r["avgTemp"])["shortName"],
        "mostResilient": max(regions, key=lambda r: r["climateScore"])["shortName"],
        "leastResilient": min(regions, key=lambda r: r["climateScore"])["shortName"],
        "highestRisk": max(regions, key=lambda r: r["avgHri"])["shortName"],
    }

    return {
        "regions": regions,
        "historical": historical,
        "forecast": forecast,
        "comparison": comparison,
        "generatedAt": pd.Timestamp.utcnow().isoformat() + "Z",
    }
