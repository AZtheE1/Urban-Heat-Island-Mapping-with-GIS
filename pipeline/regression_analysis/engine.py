"""NDVI vs LST linear regression — thesis methodology."""

import os

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from pipeline.heat_risk import (
    LST_COLUMNS,
    NDVI_COLUMNS,
    _extract_numeric_series,
    _first_present_column,
)

SUPPORTED_REGIONS = ("mirpur12", "dhaka_all", "sylhet", "rajshahi", "chittagong")

NAME_COLUMNS = ("LocationName", "locationName", "name")
SURFACE_COLUMNS = ("SurfaceType", "surfaceType")


def _build_interpretation(alpha, beta, r2, rmse, correlation, sample_count):
    """Human-readable thesis interpretation of the NDVI–LST inverse relationship."""
    if beta > 0:
        relationship = (
            f"The fitted model confirms the thesis inverse relationship: land surface "
            f"temperature decreases as vegetation density (NDVI) increases. Each +0.1 "
            f"increase in NDVI is associated with approximately {abs(beta * 0.1):.2f}°C "
            f"cooling under the linear model."
        )
    elif beta < 0:
        relationship = (
            f"The regional sample shows a positive NDVI–temperature slope (β = {beta:.4f}). "
            f"This may reflect local microclimate heterogeneity; review scatter points for "
            f"outliers or mixed surface types."
        )
    else:
        relationship = "The fitted slope is near zero; NDVI explains little linear variation in LST for this sample."

    if correlation < -0.5:
        strength = "strong inverse"
    elif correlation < -0.2:
        strength = "moderate inverse"
    elif correlation > 0.2:
        strength = "positive"
    else:
        strength = "weak"

    fit_quality = (
        f"Model fit: R² = {r2:.4f} ({100 * r2:.1f}% of LST variance explained by NDVI), "
        f"RMSE = {rmse:.4f}°C across {sample_count} observation(s)."
    )

    return {
        "summary": relationship,
        "correlationStrength": strength,
        "pearsonCorrelation": round(correlation, 4),
        "fitQuality": fit_quality,
        "thesisFormula": f"LST (°C) = {alpha} − ({beta} × NDVI)",
        "methodologyNote": (
            "Following thesis methodology: linear regression of land surface temperature "
            "(LST) on normalized difference vegetation index (NDVI), "
            "LST = α − (β × NDVI), where α is the intercept (bare-surface thermal baseline) "
            "and β is the vegetation cooling efficiency slope."
        ),
    }


def compute_regression_analysis(base_dir, region="mirpur12"):
    """
    Compute NDVI–LST linear regression for a regional calculated dataset.

    Returns scatter observations, fitted regression line, and thesis statistics.
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
    lst = _extract_numeric_series(df, LST_COLUMNS)
    ndvi = _extract_numeric_series(df, NDVI_COLUMNS)

    name_col = _first_present_column(df, NAME_COLUMNS)
    surface_col = _first_present_column(df, SURFACE_COLUMNS)

    valid_mask = lst.notna() & ndvi.notna()
    if valid_mask.sum() < 2:
        raise ValueError(
            f"At least two valid NDVI/LST pairs required for regression in region: {region}."
        )

    x = ndvi[valid_mask].to_numpy(dtype=float)
    y = lst[valid_mask].to_numpy(dtype=float)

    model = LinearRegression()
    model.fit(x.reshape(-1, 1), y)
    y_pred = model.predict(x.reshape(-1, 1))

    raw_slope = float(model.coef_[0])
    alpha = round(float(model.intercept_), 4)
    beta = round(-raw_slope, 4)

    r2 = round(float(r2_score(y, y_pred)), 4)
    rmse = round(float(np.sqrt(mean_squared_error(y, y_pred))), 4)
    mae = round(float(mean_absolute_error(y, y_pred)), 4)
    correlation = float(np.corrcoef(x, y)[0, 1]) if len(x) > 1 else 0.0

    ndvi_min = float(x.min())
    ndvi_max = float(x.max())
    line_ndvi = np.linspace(ndvi_min, ndvi_max, 40)
    line_lst = model.predict(line_ndvi.reshape(-1, 1))

    observations = []
    valid_indices = df.index[valid_mask]
    for i, idx in enumerate(valid_indices):
        point = {
            "ndvi": round(float(x[i]), 4),
            "lst": round(float(y[i]), 4),
            "predictedLst": round(float(y_pred[i]), 4),
            "residual": round(float(y[i] - y_pred[i]), 4),
        }
        if name_col and pd.notna(df.loc[idx, name_col]):
            point["locationName"] = str(df.loc[idx, name_col])
        if surface_col and pd.notna(df.loc[idx, surface_col]):
            point["surfaceType"] = str(df.loc[idx, surface_col])
        if "Latitude" in df.columns and pd.notna(df.loc[idx, "Latitude"]):
            point["lat"] = round(float(df.loc[idx, "Latitude"]), 6)
        if "Longitude" in df.columns and pd.notna(df.loc[idx, "Longitude"]):
            point["lng"] = round(float(df.loc[idx, "Longitude"]), 6)
        observations.append(point)

    interpretation = _build_interpretation(
        alpha, beta, r2, rmse, correlation, len(observations)
    )

    return {
        "region": region,
        "methodology": {
            "formula": "LST = α − (β × NDVI)",
            "ndviDefinition": "NDVI = (NIR − Red) / (NIR + Red)",
            "model": "sklearn.linear_model.LinearRegression",
        },
        "sampleCount": len(observations),
        "statistics": {
            "alphaIntercept": alpha,
            "betaSlope": beta,
            "rawSlope": round(raw_slope, 4),
            "r2Score": r2,
            "rmse": rmse,
            "mae": mae,
            "pearsonCorrelation": round(correlation, 4),
        },
        "formulaDisplay": f"Temperature = {alpha} − ({beta} × NDVI)",
        "interpretation": interpretation,
        "observations": observations,
        "regressionLine": [
            {"ndvi": round(float(ndvi_val), 4), "predictedLst": round(float(lst_val), 4)}
            for ndvi_val, lst_val in zip(line_ndvi, line_lst)
        ],
        "ndviRange": {"min": round(ndvi_min, 4), "max": round(ndvi_max, 4)},
        "lstRange": {"min": round(float(y.min()), 4), "max": round(float(y.max()), 4)},
    }
