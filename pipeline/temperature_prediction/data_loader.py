"""Load and prepare historical temperature time series for forecasting."""

import json
import os

import pandas as pd

HISTORICAL_FILENAME = "mirpur_historical_temperatures.csv"
UNIFIED_FILENAME = "mirpur_unified_environmental_data.csv"
MIN_ANNUAL_MEAN_TEMP = 5.0
MAX_ANNUAL_MEAN_TEMP = 55.0


def _annual_means_from_historical_csv(csv_path):
    df = pd.read_csv(csv_path, parse_dates=["date"])
    df["year"] = df["date"].dt.year
    annual = df.groupby("year")["mean_temp_C"].mean()
    annual = annual[
        (annual >= MIN_ANNUAL_MEAN_TEMP) & (annual <= MAX_ANNUAL_MEAN_TEMP)
    ]
    return annual.sort_index()


def _annual_means_from_unified_csv(csv_path):
    df = pd.read_csv(csv_path)
    if "Observation_Time" not in df.columns:
        return pd.Series(dtype=float)

    df["year"] = pd.to_datetime(df["Observation_Time"]).dt.year
    annual = df.groupby("year")["mean_temp_C"].mean()
    annual = annual[
        (annual >= MIN_ANNUAL_MEAN_TEMP) & (annual <= MAX_ANNUAL_MEAN_TEMP)
    ]
    return annual.sort_index()


def load_annual_temperature_series(base_dir):
    """
    Build an annual temperature series from available historical records.

    Priority: daily historical CSV, then unified environmental observations.
    """
    field_data_dir = os.path.join(base_dir, "field_data")
    historical_path = os.path.join(field_data_dir, HISTORICAL_FILENAME)
    unified_path = os.path.join(field_data_dir, UNIFIED_FILENAME)

    if os.path.exists(historical_path):
        annual = _annual_means_from_historical_csv(historical_path)
        if not annual.empty:
            return annual, "mirpur_historical_temperatures.csv"

    if os.path.exists(unified_path):
        annual = _annual_means_from_unified_csv(unified_path)
        if not annual.empty:
            return annual, "mirpur_unified_environmental_data.csv"

    raise FileNotFoundError(
        "No historical temperature records found. "
        f"Expected {HISTORICAL_FILENAME} or {UNIFIED_FILENAME} under field_data/."
    )


def load_regional_baseline_temperature(base_dir, region):
    """
    Load the current regional temperature baseline from precomputed ML metrics.

    Falls back to the latest observed annual mean when metrics are unavailable.
    """
    metrics_path = os.path.join(base_dir, "ml_models", f"{region}_reg_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as handle:
            metrics = json.load(handle)
        avg_temp = metrics.get("avg_temp")
        if avg_temp is not None:
            return float(avg_temp), metrics.get("region_name", region.capitalize())

    calculated_path = os.path.join(base_dir, "field_data", f"{region}_data_calculated.csv")
    if os.path.exists(calculated_path):
        df = pd.read_csv(calculated_path)
        if "Temperature" in df.columns and not df["Temperature"].empty:
            return round(float(df["Temperature"].mean()), 4), region.capitalize()

    return None, region.capitalize()
