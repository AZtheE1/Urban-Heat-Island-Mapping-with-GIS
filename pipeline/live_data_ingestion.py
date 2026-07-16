import os
import requests  # type: ignore[import]
import pandas as pd
from typing import Optional


def fetch_live_weather(lat: float, lng: float) -> Optional[dict]:
    """Fetches real-time weather for a coordinate via the free Open-Meteo API."""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lng}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature"
        f",precipitation,wind_speed_10m&timezone=auto"
    )
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("current", {})
            return {
                "mean_temp_C": data.get("temperature_2m", 0.0),
                "humidity_pct": data.get("relative_humidity_2m", 0.0),
                "heat_index_C": data.get("apparent_temperature", 0.0),
                "rainfall_mm": data.get("precipitation", 0.0),
                "wind_speed_kmh": data.get("wind_speed_10m", 0.0),
            }
    except Exception as e:
        print(f"Error fetching live weather for ({lat}, {lng}): {e}")
    return None


def update_dataset_with_live_data(csv_path: str) -> pd.DataFrame:
    """
    Reads an existing dataset, fetches live weather per unique coordinate via
    Open-Meteo, and updates the DataFrame column-wise (no tuple-key loc access).
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cannot find dataset at {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"Fetching live weather for {len(df)} rows in {os.path.basename(csv_path)}...")

    # Deduplicate API calls by coordinate pair
    unique_coords = df[["Latitude", "Longitude"]].drop_duplicates()
    coord_cache: dict[tuple, dict] = {}
    for _, row in unique_coords.iterrows():
        coord = (float(row["Latitude"]), float(row["Longitude"]))
        result = fetch_live_weather(coord[0], coord[1])
        if result:
            coord_cache[coord] = result

    # Build a helper column for joining, then assign each weather field vectorised
    coord_keys = list(zip(df["Latitude"].astype(float), df["Longitude"].astype(float)))
    coord_series = pd.Series(coord_keys, index=df.index)
    for field in ("mean_temp_C", "humidity_pct", "heat_index_C", "rainfall_mm", "wind_speed_kmh"):
        live_values: pd.Series = coord_series.map(lambda c: coord_cache.get(c, {}).get(field))  # type: ignore[arg-type]
        fallback = df[field] if field in df.columns else pd.Series(0.0, index=df.index)
        df[field] = live_values.fillna(fallback)

    df.to_csv(csv_path, index=False)
    print("Live data update complete.")
    return df
