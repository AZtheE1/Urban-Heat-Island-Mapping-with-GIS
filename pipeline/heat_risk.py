"""
Heat Risk Index (HRI) calculation module.

Combines normalized Land Surface Temperature (LST) and NDVI to produce a
composite heat-exposure score and categorical risk level for each location.
"""

import numpy as np
import pandas as pd

LST_MIN = 10.0
LST_MAX = 65.0
NDVI_MIN = -0.3
NDVI_MAX = 0.8

RISK_THRESHOLDS = (
    ("Very Low", 0.0, 0.2),
    ("Low", 0.2, 0.4),
    ("Moderate", 0.4, 0.6),
    ("High", 0.6, 0.8),
    ("Extreme", 0.8, 1.0001),
)

LST_COLUMNS = ("Temperature", "LST_C", "mean_temp_C", "heat_index_C")
NDVI_COLUMNS = ("Calculated_NDVI", "NDVI")
LAT_COLUMNS = ("Latitude", "lat")
LNG_COLUMNS = ("Longitude", "lng", "lon")


def min_max_normalize(values, vmin, vmax):
    """Scale values to [0, 1] using fixed physical bounds."""
    span = vmax - vmin
    if span == 0:
        return np.zeros_like(values, dtype=float)
    normalized = (values - vmin) / span
    return np.clip(normalized, 0.0, 1.0)


def classify_risk_level(heat_risk_index):
    """Map a normalized HRI score to one of five risk categories."""
    for label, lower, upper in RISK_THRESHOLDS:
        if lower <= heat_risk_index < upper:
            return label
    return "Extreme"


def _first_present_column(df, candidates):
    for column in candidates:
        if column in df.columns:
            return column
    return None


def _extract_numeric_series(df, candidates):
    column = _first_present_column(df, candidates)
    if column is None:
        raise ValueError(
            f"Required column missing. Expected one of: {', '.join(candidates)}"
        )
    return pd.to_numeric(df[column], errors="coerce")


def compute_heat_risk_from_dataframe(df):
    """
    Compute Heat Risk Index records from a calculated regional DataFrame.

    Normalization uses project-wide LST and NDVI bounds so scores remain
    comparable across regions. HRI = norm_lst * (1 - norm_ndvi).
    """
    if df.empty:
        return []

    lat_col = _first_present_column(df, LAT_COLUMNS)
    lng_col = _first_present_column(df, LNG_COLUMNS)
    if lat_col is None or lng_col is None:
        raise ValueError("Latitude and Longitude columns are required.")

    lst = _extract_numeric_series(df, LST_COLUMNS)
    ndvi = _extract_numeric_series(df, NDVI_COLUMNS)
    lat = pd.to_numeric(df[lat_col], errors="coerce")
    lng = pd.to_numeric(df[lng_col], errors="coerce")

    norm_lst = min_max_normalize(lst.to_numpy(dtype=float), LST_MIN, LST_MAX)
    norm_ndvi = min_max_normalize(ndvi.to_numpy(dtype=float), NDVI_MIN, NDVI_MAX)
    hri = norm_lst * (1.0 - norm_ndvi)

    records = []
    for idx in df.index:
        if pd.isna(lat.iloc[idx]) or pd.isna(lng.iloc[idx]):
            continue
        if pd.isna(lst.iloc[idx]) or pd.isna(ndvi.iloc[idx]):
            continue

        heat_risk_index = float(hri[idx])
        records.append(
            {
                "lat": round(float(lat.iloc[idx]), 6),
                "lng": round(float(lng.iloc[idx]), 6),
                "lst": round(float(lst.iloc[idx]), 4),
                "ndvi": round(float(ndvi.iloc[idx]), 4),
                "heatRiskIndex": round(heat_risk_index, 4),
                "riskLevel": classify_risk_level(heat_risk_index),
            }
        )

    return records
