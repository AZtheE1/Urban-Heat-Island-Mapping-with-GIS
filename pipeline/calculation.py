import numpy as np
import pandas as pd


SURFACE_REFLECTANCE_PRESETS = {
    "Asphalt": {"red": 0.165, "nir": 0.105, "heat_offset": 3.2},
    "Concrete": {"red": 0.190, "nir": 0.145, "heat_offset": 2.4},
    "Vegetation": {"red": 0.085, "nir": 0.390, "heat_offset": -2.6},
    "Water Body": {"red": 0.070, "nir": 0.045, "heat_offset": -3.4},
    "Bare Soil": {"red": 0.210, "nir": 0.180, "heat_offset": 1.4},
    "Mixed": {"red": 0.155, "nir": 0.175, "heat_offset": 0.7},
}

TRAFFIC_HEAT_OFFSETS = {
    "Low": -0.3,
    "Medium": 0.5,
    "High": 1.2,
}

def compute_ndvi(nir, red):
    """
    Normalized Difference Vegetation Index (NDVI) formula:
    NDVI = (NIR - Red) / (NIR + Red)
    """
    denominator = nir + red
    if isinstance(nir, (int, float, np.number)):
        return (nir - red) / denominator if denominator != 0 else 0.0
    
    # Pandas Series implementation
    return np.where(denominator != 0, (nir - red) / denominator, 0.0)

def compute_lst(ndvi, alpha, beta):
    """
    Land Surface Temperature predicted equation based on vegetation density:
    LST = alpha - (beta * NDVI)
    """
    return alpha - (beta * ndvi)

def estimate_reflectance_from_ground_data(df):
    """
    Estimates Red and NIR reflectance from surface category plus observed
    weather context. This is a project-stage proxy until raw satellite bands
    are available.
    """
    surface = df["SurfaceType"].fillna("Mixed")
    preset_red = surface.map(
        lambda value: SURFACE_REFLECTANCE_PRESETS.get(
            value, SURFACE_REFLECTANCE_PRESETS["Mixed"]
        )["red"]
    )
    preset_nir = surface.map(
        lambda value: SURFACE_REFLECTANCE_PRESETS.get(
            value, SURFACE_REFLECTANCE_PRESETS["Mixed"]
        )["nir"]
    )

    humidity_norm = ((df["humidity_pct"] - 70.0) / 100.0).clip(-0.3, 0.3)
    rain_norm = (df["rainfall_mm"] / 150.0).clip(0.0, 0.35)
    temp_norm = ((df["mean_temp_C"] - 26.0) / 20.0).clip(-0.4, 0.4)

    red = preset_red + (0.018 * temp_norm) - (0.012 * rain_norm)
    nir = preset_nir + (0.040 * humidity_norm) + (0.030 * rain_norm)

    output = df.copy()
    output["Red"] = red.clip(0.02, 0.60).round(5)
    output["NIR"] = nir.clip(0.02, 0.75).round(5)
    output["NDVI"] = np.round(compute_ndvi(output["NIR"], output["Red"]), 5)
    return output

def estimate_lst_from_ground_data(df):
    """
    Estimates Land Surface Temperature in Celsius from observed weather,
    surface heat retention, traffic, wind cooling, and calculated NDVI.
    """
    surface_offset = df["SurfaceType"].map(
        lambda value: SURFACE_REFLECTANCE_PRESETS.get(
            value, SURFACE_REFLECTANCE_PRESETS["Mixed"]
        )["heat_offset"]
    )
    traffic_offset = df["TrafficDensity"].map(TRAFFIC_HEAT_OFFSETS).fillna(0.0)

    heat_index_component = (df["heat_index_C"] - df["mean_temp_C"]).clip(-5.0, 20.0)
    wind_cooling = (df["wind_speed_kmh"] * 0.045).clip(0.0, 1.8)
    vegetation_cooling = (df["NDVI"].clip(-0.3, 0.8) * 3.0)

    lst = (
        df["mean_temp_C"]
        + surface_offset
        + traffic_offset
        + (0.22 * heat_index_component)
        - wind_cooling
        - vegetation_cooling
    )

    output = df.copy()
    output["LST_C"] = lst.clip(10.0, 65.0).round(3)
    output["Temperature"] = output["LST_C"]
    return output

def calculate_remote_sensing_indices(df):
    """
    Produces calculation-stage columns needed by the UHI pipeline:
    Red, NIR, NDVI, LST_C, Temperature, and Calculated_NDVI.
    """
    required_columns = {
        "SurfaceType",
        "TrafficDensity",
        "mean_temp_C",
        "humidity_pct",
        "rainfall_mm",
        "wind_speed_kmh",
        "heat_index_C",
    }
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required calculation columns: {missing}")

    calculated = estimate_reflectance_from_ground_data(df)
    calculated["Calculated_NDVI"] = np.round(compute_ndvi(
        calculated["NIR"], calculated["Red"]
    ), 5)
    calculated = estimate_lst_from_ground_data(calculated)

    return calculated

def summarize_calculated_indices(df):
    hottest_idx = df["LST_C"].idxmax()
    coolest_idx = df["LST_C"].idxmin()

    return {
        "rows": len(df),
        "avg_lst_c": round(float(df["LST_C"].mean()), 3),
        "avg_ndvi": round(float(df["NDVI"].mean()), 5),
        "min_ndvi": round(float(df["NDVI"].min()), 5),
        "max_ndvi": round(float(df["NDVI"].max()), 5),
        "peak_hotspot": {
            "name": str(df.loc[hottest_idx, "LocationName"]),
            "lst_c": float(df.loc[hottest_idx, "LST_C"]),
            "lat": float(df.loc[hottest_idx, "Latitude"]),
            "lng": float(df.loc[hottest_idx, "Longitude"]),
        },
        "peak_coolspot": {
            "name": str(df.loc[coolest_idx, "LocationName"]),
            "lst_c": float(df.loc[coolest_idx, "LST_C"]),
            "lat": float(df.loc[coolest_idx, "Latitude"]),
            "lng": float(df.loc[coolest_idx, "Longitude"]),
        },
    }

def perform_mathematical_calculations(df):
    """
    Computes environmental indicators and runs summary aggregation checks on the dataset.
    """
    if "NDVI" not in df.columns:
        df = calculate_remote_sensing_indices(df)
    elif "NIR" not in df.columns or "Red" not in df.columns:
        # Synthesize physical NIR and Red reflectances based on the existing NDVI:
        # NDVI = (NIR - Red)/(NIR + Red) => Red = 0.1, NIR = Red * (1 + NDVI) / (1 - NDVI)
        red_base = 0.1
        df["Red"] = red_base
        df["NIR"] = red_base * (1 + df["NDVI"]) / (1 - df["NDVI"])
        
    # Apply standard NDVI calculation function
    df["Calculated_NDVI"] = compute_ndvi(df["NIR"], df["Red"])
    
    # Calculate dataset summaries
    avg_temp = round(float(df["Temperature"].mean()), 2)
    hottest_idx = df["Temperature"].idxmax()
    coolest_idx = df["Temperature"].idxmin()
    
    peak_hotspot = {
        "name": str(df.loc[hottest_idx, "LocationName"]),
        "temp": float(df.loc[hottest_idx, "Temperature"]),
        "lat": float(df.loc[hottest_idx, "Latitude"]),
        "lng": float(df.loc[hottest_idx, "Longitude"])
    }
    
    peak_coolspot = {
        "name": str(df.loc[coolest_idx, "LocationName"]),
        "temp": float(df.loc[coolest_idx, "Temperature"]),
        "lat": float(df.loc[coolest_idx, "Latitude"]),
        "lng": float(df.loc[coolest_idx, "Longitude"])
    }
    
    results = {
        "avg_temp": avg_temp,
        "peak_hotspot": peak_hotspot,
        "peak_coolspot": peak_coolspot
    }
    
    return df, results

def create_location_labels(df):
    """
    Constructs descriptive scientific labels for the locations by combining
    physical coordinates with local morphology descriptors.
    """
    output = df.copy()
    if "Time_of_Day" not in output.columns:
        if "Observation_Hour" in output.columns and "Observation_Minute" in output.columns:
            output["Time_of_Day"] = output.apply(lambda r: f"{int(r['Observation_Hour']):02d}:{int(r['Observation_Minute']):02d}", axis=1)
        else:
            output["Time_of_Day"] = "12:00"
            
    output['Location_Label'] = (
        output['LocationName'] + "\n" +
        "[" + output['SurfaceType'] + " | Traffic: " + output['TrafficDensity'] + " | " + output['Time_of_Day'] + "]"
    )
    return output

def calculate_hazard_days(df, hazard_threshold=45.0):
    """
    Defines a critical environmental health hazard threshold.
    Returns the exact number of days per year that citizens were exposed
    to these dangerous conditions across different urban zones.
    """
    if "Year" not in df.columns and "Observation_Year" in df.columns:
        df["Year"] = df["Observation_Year"]
        
    df['Is_Dangerous_Day'] = df['heat_index_C'] >= hazard_threshold
    danger_counts = df.groupby(['LocationName', 'SurfaceType', 'Year'])['Is_Dangerous_Day'].sum().reset_index()
    danger_counts = danger_counts.rename(columns={'Is_Dangerous_Day': 'Dangerous_Days_Count'})
    danger_counts['Profile'] = danger_counts['LocationName'] + " (" + danger_counts['SurfaceType'] + ")"
    return danger_counts
