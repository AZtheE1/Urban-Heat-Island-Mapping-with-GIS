"""Hotspot ranking and sorting logic."""

import pandas as pd

from pipeline.heat_risk import (
    LAT_COLUMNS,
    LNG_COLUMNS,
    compute_heat_risk_from_dataframe,
    _first_present_column,
)

from .constants import (
    DEFAULT_LIMIT,
    DEFAULT_SORT,
    SORT_BY_HEAT_RISK,
    SORT_BY_TEMPERATURE,
    SORT_OPTIONS,
)
from .data_loader import load_all_regional_dataframes, load_regional_display_name

NAME_COLUMNS = ("LocationName", "locationName", "name")


def _build_name_lookup(df):
    lat_col = _first_present_column(df, LAT_COLUMNS)
    lng_col = _first_present_column(df, LNG_COLUMNS)
    name_col = _first_present_column(df, NAME_COLUMNS)
    if not lat_col or not lng_col or not name_col:
        return {}

    lookup = {}
    for idx in df.index:
        if name_col not in df.columns:
            continue
        name = df.loc[idx, name_col]
        lat = df.loc[idx, lat_col]
        lng = df.loc[idx, lng_col]
        if pd.notna(name) and pd.notna(lat) and pd.notna(lng):
            lookup[(round(float(lat), 6), round(float(lng), 6))] = str(name)
    return lookup


def _build_location_record(region, region_name, heat_record, name_lookup):
    coordinate_key = (heat_record["lat"], heat_record["lng"])
    return {
        "region": region,
        "regionName": region_name,
        "locationName": name_lookup.get(coordinate_key),
        "lat": heat_record["lat"],
        "lng": heat_record["lng"],
        "temperature": heat_record["lst"],
        "ndvi": heat_record["ndvi"],
        "heatRiskIndex": heat_record["heatRiskIndex"],
        "riskLevel": heat_record["riskLevel"],
    }


def _sort_key(record, sort_by):
    if sort_by == SORT_BY_HEAT_RISK:
        return (record["heatRiskIndex"], record["temperature"])
    return (record["temperature"], record["heatRiskIndex"])


def _rank_region_summaries(locations):
    """Rank analyzed regions by average temperature and average HRI."""
    regional_groups = {}
    for location in locations:
        regional_groups.setdefault(location["region"], []).append(location)

    summaries = []
    for region, items in regional_groups.items():
        avg_temperature = round(sum(item["temperature"] for item in items) / len(items), 4)
        avg_hri = round(sum(item["heatRiskIndex"] for item in items) / len(items), 4)
        summaries.append(
            {
                "region": region,
                "regionName": items[0]["regionName"],
                "locationCount": len(items),
                "averageTemperature": avg_temperature,
                "averageHeatRiskIndex": avg_hri,
            }
        )

    by_temperature = sorted(
        summaries,
        key=lambda item: (item["averageTemperature"], item["averageHeatRiskIndex"]),
        reverse=True,
    )
    by_heat_risk = sorted(
        summaries,
        key=lambda item: (item["averageHeatRiskIndex"], item["averageTemperature"]),
        reverse=True,
    )

    for rank, item in enumerate(by_temperature, start=1):
        item["temperatureRank"] = rank
    for rank, item in enumerate(by_heat_risk, start=1):
        item["heatRiskRank"] = rank

    return sorted(summaries, key=lambda item: item["temperatureRank"])


def rank_hotspots(
    base_dir,
    sort_by=DEFAULT_SORT,
    limit=DEFAULT_LIMIT,
    regions=None,
):
    """
    Rank locations across all analyzed regions and return the hottest hotspots.

    Primary sort is controlled by `sort_by` (temperature or heatRiskIndex).
    Secondary sort uses the other metric to break ties.
    """
    if sort_by not in SORT_OPTIONS:
        available = ", ".join(sorted(SORT_OPTIONS))
        raise ValueError(f"Unsupported sortBy value '{sort_by}'. Available: {available}")

    limit = max(1, int(limit))
    regional_frames = load_all_regional_dataframes(base_dir, regions=regions)

    all_locations = []
    for region, dataframe in regional_frames.items():
        region_name = load_regional_display_name(base_dir, region)
        dataframe = dataframe.reset_index(drop=True)
        name_lookup = _build_name_lookup(dataframe)
        heat_records = compute_heat_risk_from_dataframe(dataframe)

        for heat_record in heat_records:
            all_locations.append(
                _build_location_record(region, region_name, heat_record, name_lookup)
            )

    sorted_locations = sorted(
        all_locations,
        key=lambda record: _sort_key(record, sort_by),
        reverse=True,
    )

    top_hotspots = []
    for rank, record in enumerate(sorted_locations[:limit], start=1):
        top_hotspots.append({"rank": rank, **record})

    region_rankings = _rank_region_summaries(all_locations)

    return {
        "sortBy": sort_by,
        "limit": limit,
        "totalLocationsAnalyzed": len(all_locations),
        "regionsAnalyzed": len(regional_frames),
        "regionRankings": region_rankings,
        "hotspots": top_hotspots,
    }
