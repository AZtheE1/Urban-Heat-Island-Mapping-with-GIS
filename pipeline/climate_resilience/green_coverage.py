"""Green coverage estimation from surface types and NDVI."""

SURFACE_GREEN_WEIGHTS = {
    "Vegetation": 100.0,
    "Water Body": 100.0,
    "Mixed": 50.0,
    "Bare Soil": 20.0,
    "Concrete": 10.0,
    "Asphalt": 5.0,
}

DEFAULT_SURFACE_WEIGHT = 30.0


def surface_green_weight(surface_type):
    """Map a surface category to an estimated local green-coverage percentage."""
    return SURFACE_GREEN_WEIGHTS.get(str(surface_type or "").strip(), DEFAULT_SURFACE_WEIGHT)


def estimate_location_green_coverage(surface_type, ndvi, ndvi_min=-0.3, ndvi_max=0.8):
    """
    Blend surface-type coverage with NDVI-derived canopy density.

    Surface weight captures land-use green infrastructure; NDVI captures
    observed vegetation health/density at the observation point.
    """
    surface_pct = surface_green_weight(surface_type)
    ndvi_span = ndvi_max - ndvi_min
    ndvi_pct = 0.0
    if ndvi_span > 0:
        ndvi_pct = max(0.0, min(100.0, ((float(ndvi) - ndvi_min) / ndvi_span) * 100.0))
    return round((0.55 * surface_pct) + (0.45 * ndvi_pct), 2)


def compute_regional_green_coverage(df, ndvi_series):
    """Return average green coverage percentage across valid regional records."""
    if df.empty:
        return 0.0

    values = []
    for idx in df.index:
        if idx >= len(ndvi_series) or ndvi_series.iloc[idx] != ndvi_series.iloc[idx]:
            continue
        surface_type = df.loc[idx, "SurfaceType"] if "SurfaceType" in df.columns else None
        values.append(
            estimate_location_green_coverage(surface_type, float(ndvi_series.iloc[idx]))
        )

    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)
