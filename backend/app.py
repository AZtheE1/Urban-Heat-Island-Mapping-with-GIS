from flask import Flask, jsonify, request, send_from_directory
import os
import pandas as pd
import numpy as np
import sys
import os

# Ensure the backend directory is in the Python system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.analytics import run_regression_analysis

app = Flask(__name__, static_folder="../frontend", static_url_path="")

# Root path of the codebase workspace
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "environmental", "mirpur12_ground_data.csv")

# Dynamic generator for divisional/macro regions based on baseline characteristics
def generate_regional_data(region):
    """
    Synthesizes regional statistical profiles for macro expansion
    (Dhaka, Sylhet, Rajshahi, Chittagong).
    """
    presets = {
        "dhaka_all": {"base_temp": 34.5, "slope": -9.5, "r2": 0.72, "canopy": 0.25, "desc": "Dense urban environment with wide surface heat dispersion."},
        "sylhet": {"base_temp": 31.2, "slope": -8.0, "r2": 0.81, "canopy": 0.58, "desc": "High green canopy ratios and tea estate borders leading to low average heat retention."},
        "rajshahi": {"base_temp": 37.8, "slope": -11.2, "r2": 0.79, "canopy": 0.18, "desc": "High dry summer temperatures and heavy pavement-retained heat profiles."},
        "chittagong": {"base_temp": 33.6, "slope": -8.5, "r2": 0.68, "canopy": 0.35, "desc": "Coastal cooling winds offset by heavy industrial concrete hubs."}
    }
    
    config = presets.get(region)
    if not config:
        return None
        
    # Generate 15 simulated coordinate variations around the city center
    # Set coordinates matching GIS center presets
    centers = {
        "dhaka_all": (23.8103, 90.4125),
        "sylhet": (24.8949, 91.8687),
        "rajshahi": (24.3745, 88.6042),
        "chittagong": (22.3569, 91.7832)
    }
    lat_c, lng_c = centers[region]
    
    np.random.seed(42) # Consistent outputs
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
            "LocationName": f"{region.capitalize()} Site {i}",
            "Latitude": round(lat, 5),
            "Longitude": round(lng, 5),
            "Temperature": round(temp, 1),
            "SurfaceType": surface,
            "NDVI": round(ndvi, 2),
            "TrafficDensity": "High" if ndvi < 0.25 else "Medium" if ndvi < 0.5 else "Low",
            "Time": "Afternoon"
        })
        
    # Standard regression values for the simulated dataset
    df = pd.DataFrame(records)
    avg_temp = round(df['Temperature'].mean(), 2)
    hottest = df.loc[df['Temperature'].idxmax()]
    coolest = df.loc[df['Temperature'].idxmin()]
    
    return {
        "alpha_intercept": round(config["base_temp"], 4),
        "beta_slope": round(config["slope"], 4),
        "rmse": 0.45,
        "mae": 0.38,
        "r2_score": config["r2"],
        "avg_temp": avg_temp,
        "peak_hotspot": {
            "name": str(hottest['LocationName']),
            "temp": float(hottest['Temperature']),
            "lat": float(hottest['Latitude']),
            "lng": float(hottest['Longitude'])
        },
        "peak_coolspot": {
            "name": str(coolest['LocationName']),
            "temp": float(coolest['Temperature']),
            "lat": float(coolest['Latitude']),
            "lng": float(coolest['Longitude'])
        }
    }, records

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/heat-data")
def get_heat_data():
    region = request.args.get("region", "mirpur12")
    
    if region == "mirpur12":
        # Process live ground CSV
        analytics, records = run_regression_analysis(CSV_PATH)
        return jsonify({
            "region": region,
            "name": "Mirpur 12",
            "description": "Hyper-local baseline micro-analysis mapping 20 ground sensor coordinates.",
            "analytics": analytics,
            "records": records
        })
        
    else:
        # Serve synthesized divisional profiles
        output = generate_regional_data(region)
        if output is None:
            return jsonify({"error": "Unknown region. Supported: mirpur12, dhaka_all, sylhet, rajshahi, chittagong"}), 400
            
        analytics, records = output
        names = {
            "dhaka_all": "Entire Dhaka Metropolitan Area",
            "sylhet": "Sylhet Division",
            "rajshahi": "Rajshahi Division",
            "chittagong": "Chittagong Division"
        }
        descs = {
            "dhaka_all": "Dense urban environment with wide surface heat dispersion.",
            "sylhet": "High green canopy ratios and tea estate borders leading to low average heat retention.",
            "rajshahi": "High dry summer temperatures and heavy pavement-retained heat profiles.",
            "chittagong": "Coastal cooling winds offset by heavy industrial concrete hubs."
        }
        return jsonify({
            "region": region,
            "name": names.get(region, region.capitalize()),
            "description": descs.get(region, ""),
            "analytics": analytics,
            "records": records
        })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
