"""Regression-based temperature estimation from NDVI."""

import json
import os


def load_regression_coefficients(base_dir, region):
    """Load precomputed linear regression coefficients for a region."""
    metrics_path = os.path.join(base_dir, "ml_models", f"{region}_reg_metrics.json")
    if not os.path.exists(metrics_path):
        raise FileNotFoundError(
            f"Regression metrics not found for region: {region}. Run main.py first."
        )

    with open(metrics_path, "r", encoding="utf-8") as handle:
        metrics = json.load(handle)

    alpha = metrics.get("alpha_intercept")
    beta = metrics.get("beta_slope")
    if alpha is None or beta is None:
        raise ValueError(f"Regression coefficients missing for region: {region}")

    linear = metrics.get("linear_regression", {})
    return {
        "alpha": float(alpha),
        "beta": float(beta),
        "r2Score": linear.get("r2_score", metrics.get("r2_score")),
        "rmse": linear.get("rmse", metrics.get("rmse")),
        "formula": linear.get(
            "formula",
            f"Temperature = {round(alpha, 2)} - ({round(beta, 2)} * NDVI)",
        ),
        "regionName": metrics.get("region_name", region.replace("_", " ").title()),
    }


def estimate_temperature(alpha, beta, ndvi):
    """
    Predict land surface temperature using the project regression model.

    Temperature = alpha - (beta * NDVI)
    """
    return float(alpha) - (float(beta) * float(ndvi))
