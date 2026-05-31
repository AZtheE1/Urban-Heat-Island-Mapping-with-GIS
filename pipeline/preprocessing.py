import os
import pandas as pd
import numpy as np

# Baseline characteristics for divisional expansions
REGIONAL_PRESETS = {
    "dhaka_all": {
        "name": "Entire Dhaka Metropolitan Area",
        "base_temp": 34.5,
        "slope": 9.5,
        "r2": 0.72,
        "canopy": 0.25,
        "center": (23.8103, 90.4125),
        "desc": "Dense urban environment with wide surface heat dispersion."
    },
    "sylhet": {
        "name": "Sylhet Division",
        "base_temp": 31.2,
        "slope": 8.0,
        "r2": 0.81,
        "canopy": 0.58,
        "center": (24.8949, 91.8687),
        "desc": "High green canopy ratios and tea estate borders leading to low average heat retention."
    },
    "rajshahi": {
        "name": "Rajshahi Division",
        "base_temp": 37.8,
        "slope": 11.2,
        "r2": 0.79,
        "canopy": 0.18,
        "center": (24.3745, 88.6042),
        "desc": "High dry summer temperatures and heavy pavement-retained heat profiles."
    },
    "chittagong": {
        "name": "Chittagong Division",
        "base_temp": 33.6,
        "slope": 8.5,
        "r2": 0.68,
        "canopy": 0.35,
        "center": (22.3569, 91.7832),
        "desc": "Coastal cooling winds offset by heavy industrial concrete hubs."
    }
}

def load_regional_data(region_id, csv_path):
    """
    Ingests environmental data. Loads ground CSV for Mirpur 12 baseline,
    or generates simulated environmental telemetry for divisional presets.
    """
    if region_id == "mirpur12":
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Mirpur 12 baseline CSV not found at {csv_path}")
        df = pd.read_csv(csv_path)
        meta = {
            "region": region_id,
            "name": "Mirpur 12",
            "description": "Hyper-local baseline micro-analysis mapping 20 ground sensor coordinates."
        }
        return df, meta

    elif region_id in REGIONAL_PRESETS:
        config = REGIONAL_PRESETS[region_id]
        lat_c, lng_c = config["center"]
        
        np.random.seed(42)  # Consistent randomized dataset matching seed 42
        records = []
        for i in range(1, 16):
            ndvi = float(np.random.uniform(0.05, 0.8))
            # Linear response: temp = intercept - (slope * ndvi) + noise
            temp = config["base_temp"] - (config["slope"] * (0.8 - ndvi)) + np.random.normal(0, 0.5)
            lat = lat_c + np.random.uniform(-0.03, 0.03)
            lng = lng_c + np.random.uniform(-0.03, 0.03)
            
            surface = "Concrete" if ndvi < 0.2 else "Asphalt" if ndvi < 0.4 else "Vegetation" if ndvi > 0.55 else "Bare Soil"
            
            records.append({
                "LocationID": i,
                "LocationName": f"{region_id.capitalize()} Site {i}",
                "Latitude": round(lat, 5),
                "Longitude": round(lng, 5),
                "Temperature": round(temp, 1),
                "SurfaceType": surface,
                "NDVI": round(ndvi, 2),
                "TrafficDensity": "High" if ndvi < 0.25 else "Medium" if ndvi < 0.5 else "Low",
                "Time": "Afternoon"
            })
            
        df = pd.DataFrame(records)
        meta = {
            "region": region_id,
            "name": config["name"],
            "description": config["desc"]
        }
        return df, meta
    else:
        raise ValueError(f"Unknown region_id: {region_id}. Supported: mirpur12, dhaka_all, sylhet, rajshahi, chittagong")
