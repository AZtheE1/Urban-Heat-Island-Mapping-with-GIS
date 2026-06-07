"""Load temperature observations for heatwave monitoring."""

import os

import pandas as pd

from pipeline.heat_risk import LST_COLUMNS, _extract_numeric_series, _first_present_column

HISTORICAL_FILENAME = "mirpur_historical_temperatures.csv"
NAME_COLUMNS = ("LocationName", "locationName", "name")
LAT_COLUMNS = ("Latitude", "lat")
LNG_COLUMNS = ("Longitude", "lng", "lon")


def _build_timestamp(row, fallback_timestamp):
    if "date" in row and pd.notna(row["date"]):
        return pd.to_datetime(row["date"]).tz_localize(None).isoformat() + "Z"
    if "Observation_Time" in row and pd.notna(row["Observation_Time"]):
        return pd.to_datetime(row["Observation_Time"]).tz_localize(None).isoformat() + "Z"
    return fallback_timestamp


def load_regional_temperature_observations(df, fallback_timestamp):
    """Extract monitorable temperature readings from a regional calculated CSV."""
    if df.empty:
        return []

    name_col = _first_present_column(df, NAME_COLUMNS)
    lat_col = _first_present_column(df, LAT_COLUMNS)
    lng_col = _first_present_column(df, LNG_COLUMNS)
    temperatures = _extract_numeric_series(df, LST_COLUMNS)

    observations = []
    for idx in df.index:
        if pd.isna(temperatures.iloc[idx]):
            continue

        location_name = None
        if name_col is not None and pd.notna(df.loc[idx, name_col]):
            location_name = str(df.loc[idx, name_col])

        lat = None
        lng = None
        if lat_col is not None and pd.notna(df.loc[idx, lat_col]):
            lat = round(float(df.loc[idx, lat_col]), 6)
        if lng_col is not None and pd.notna(df.loc[idx, lng_col]):
            lng = round(float(df.loc[idx, lng_col]), 6)

        observations.append(
            {
                "temperature": float(temperatures.iloc[idx]),
                "locationName": location_name,
                "lat": lat,
                "lng": lng,
                "timestamp": fallback_timestamp,
                "source": "regional_ground_data",
            }
        )

    return observations


def load_historical_temperature_observations(base_dir, fallback_timestamp, limit=50):
    """Load historical temperature records that exceed heatwave warning thresholds."""
    csv_path = os.path.join(base_dir, "field_data", HISTORICAL_FILENAME)
    if not os.path.exists(csv_path):
        return []

    df = pd.read_csv(csv_path, parse_dates=["date"])
    df = df.sort_values("date", ascending=False)

    observations = []
    for _, row in df.iterrows():
        timestamp = _build_timestamp(row, fallback_timestamp)
        for column in ("max_temp_C", "mean_temp_C"):
            if pd.isna(row[column]):
                continue
            temperature = float(row[column])
            if temperature <= 35.0:
                continue
            observations.append(
                {
                    "temperature": temperature,
                    "locationName": f"Historical ({column.replace('_', ' ')})",
                    "lat": None,
                    "lng": None,
                    "timestamp": timestamp,
                    "source": "historical_temperature_log",
                }
            )

    observations.sort(key=lambda item: item["temperature"], reverse=True)
    return observations[:limit]
