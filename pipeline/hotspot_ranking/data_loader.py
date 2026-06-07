"""Load regional datasets for cross-region hotspot ranking."""

import json
import os

import pandas as pd

from .constants import ANALYZED_REGIONS


def load_regional_calculated_dataframe(base_dir, region):
    """Load a precomputed regional CSV if available."""
    csv_path = os.path.join(base_dir, "field_data", f"{region}_data_calculated.csv")
    if not os.path.exists(csv_path):
        return None
    return pd.read_csv(csv_path)


def load_regional_display_name(base_dir, region):
    """Resolve human-readable region name from ML metrics when present."""
    metrics_path = os.path.join(base_dir, "ml_models", f"{region}_reg_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as handle:
            metrics = json.load(handle)
        return metrics.get("region_name", region.replace("_", " ").title())
    return region.replace("_", " ").title()


def load_all_regional_dataframes(base_dir, regions=None):
    """Load calculated datasets for all analyzed regions."""
    selected_regions = regions or ANALYZED_REGIONS
    loaded = {}

    for region in selected_regions:
        dataframe = load_regional_calculated_dataframe(base_dir, region)
        if dataframe is not None and not dataframe.empty:
            loaded[region] = dataframe

    if not loaded:
        raise FileNotFoundError(
            "No regional datasets found. Run main.py to generate field_data/*_data_calculated.csv files."
        )

    return loaded
