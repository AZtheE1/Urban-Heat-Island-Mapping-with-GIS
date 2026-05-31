import numpy as np
import pandas as pd

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

def perform_mathematical_calculations(df):
    """
    Computes environmental indicators and runs summary aggregation checks on the dataset.
    """
    # Verify required columns are present. If NIR and Red are missing, synthesize them based on NDVI
    # to demonstrate the NDVI calculation function.
    if "NIR" not in df.columns or "Red" not in df.columns:
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
