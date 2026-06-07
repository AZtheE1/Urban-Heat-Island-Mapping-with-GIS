"""Vegetation deficit scoring from LST and NDVI observations."""

import numpy as np

PRIORITY_DEFICIT_THRESHOLD = 0.45


def regional_min_max_normalize(series):
    """Scale values to [0, 1] using the min/max observed in a regional dataset."""
    vmin = float(series.min())
    vmax = float(series.max())
    if vmax == vmin:
        return np.full(len(series), 0.5, dtype=float)
    normalized = (series.to_numpy(dtype=float) - vmin) / (vmax - vmin)
    return np.clip(normalized, 0.0, 1.0)


def compute_vegetation_deficit_score(norm_lst, norm_ndvi):
    """
    Estimate vegetation deficit from normalized temperature and NDVI.

    High LST combined with low NDVI yields a higher deficit score in [0, 1].
    """
    return float(norm_lst * (1.0 - norm_ndvi))


def is_priority_area(lst, ndvi, deficit_score, regional_lst_mean, regional_ndvi_mean):
    """Flag locations with high temperature and low vegetation cover."""
    high_temperature = lst >= regional_lst_mean
    low_ndvi = ndvi <= regional_ndvi_mean
    return bool(high_temperature and low_ndvi) or deficit_score >= PRIORITY_DEFICIT_THRESHOLD
