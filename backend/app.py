from flask import Flask, jsonify, request, send_from_directory, send_file
import os
import sys
import json
import io
import pandas as pd
import numpy as np
from flask_caching import Cache
from functools import wraps

app = Flask(__name__, static_folder="../frontend", static_url_path="")
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

API_KEY = os.environ.get("API_KEY", "HACKATHON_DEMO_KEY")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get("x-api-key") or request.args.get("api_key")
        # Soft validation to avoid breaking existing frontend in hackathon demo
        if provided_key and provided_key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 403
        return f(*args, **kwargs)
    return decorated_function
# Root path of the codebase workspace
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from pipeline.heat_risk import compute_heat_risk_from_dataframe
from pipeline.temperature_prediction import predict_temperature_for_region
from pipeline.recommendations import generate_recommendations_from_dataframe
from pipeline.climate_resilience import compute_climate_resilience_from_dataframe
from pipeline.heatwave_alerts import evaluate_heatwave_alerts
from pipeline.geo_analytics import analyze_region_polygon, validate_geojson
from pipeline.hotspot_ranking import rank_hotspots, DEFAULT_LIMIT, DEFAULT_SORT
from pipeline.report_generator import generate_environmental_report, FORMAT_JSON, FORMAT_PDF, DEFAULT_FORMAT
from pipeline.green_simulation import simulate_green_growth, simulate_green_infrastructure
from pipeline.edss import generate_decision_support
from pipeline.climate_analytics import build_climate_analytics
from pipeline.thesis_analytics import (
    load_data_provenance,
    load_hybrid_forecast,
    load_model_validation,
)
from pipeline.regression_analysis import compute_regression_analysis

REGIONAL_DESCRIPTIONS = {
    "mirpur12": "Hyper-local baseline micro-analysis mapping 20 ground sensor coordinates.",
    "dhaka_all": "Dense urban environment with wide surface heat dispersion.",
    "sylhet": "High green canopy ratios and tea estate borders leading to low average heat retention.",
    "rajshahi": "High dry summer temperatures and heavy pavement-retained heat profiles.",
    "chittagong": "Coastal cooling winds offset by heavy industrial concrete hubs."
}

# Serve the satellite_data folder statically to the frontend
@app.route("/satellite_data/<path:filename>")
def serve_satellite_data(filename):
    return send_from_directory(os.path.join(BASE_DIR, "satellite_data"), filename)

# Serve the field_data folder statically if needed
@app.route("/field_data/<path:filename>")
def serve_field_data(filename):
    return send_from_directory(os.path.join(BASE_DIR, "field_data"), filename)

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/analytics")
def analytics():
    return send_from_directory(app.static_folder, "analytics.html")

@app.route("/simulation")
def simulation():
    return send_from_directory(app.static_folder, "simulation.html")

@app.route("/decisions")
def decisions():
    return send_from_directory(app.static_folder, "decisions.html")

@app.route("/reports")
def reports():
    return send_from_directory(app.static_folder, "reports.html")

@app.route("/alerts")
def alerts_page():
    return send_from_directory(app.static_folder, "alerts.html")

@app.route("/gis")
def gis_page():
    return send_from_directory(app.static_folder, "gis.html")

@app.route("/regression")
def regression_page():
    return send_from_directory(app.static_folder, "regression.html")

@app.route("/documentation")
def documentation_page():
    return send_from_directory(app.static_folder, "documentation.html")

@app.route("/api/project-documentation")
def project_documentation():
    json_path = os.path.join(BASE_DIR, "frontend", "data", "project-documentation.json")
    try:
        with open(json_path, "r", encoding="utf-8") as handle:
            return jsonify(json.load(handle))
    except FileNotFoundError:
        return jsonify({"error": "Project documentation data not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/regression-analysis")
def regression_analysis():
    region = request.args.get("region", "mirpur12")

    try:
        result = compute_regression_analysis(BASE_DIR, region=region)

        json_path = os.path.join(BASE_DIR, "ml_models", f"{region}_reg_metrics.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as handle:
                metrics = json.load(handle)
            result["name"] = metrics.get("region_name", region.capitalize())
        else:
            result["name"] = region.capitalize()

        result["description"] = REGIONAL_DESCRIPTIONS.get(
            region, "Thermal GIS mapping layer."
        )
        return jsonify(result)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/heat-data")
@cache.cached(query_string=True)
@require_api_key
def get_heat_data():
    region = request.args.get("region", "mirpur12")
    
    csv_filename = f"{region}_data_calculated.csv"
    csv_path = os.path.join(BASE_DIR, "field_data", csv_filename)
    
    json_filename = f"{region}_reg_metrics.json"
    json_path = os.path.join(BASE_DIR, "ml_models", json_filename)
    
    if not os.path.exists(csv_path) or not os.path.exists(json_path):
        return jsonify({"error": f"Data or metrics not pre-computed for region: {region}. Run main.py first."}), 400
        
    try:
        # Load records from calculated CSV
        df = pd.read_csv(csv_path)
        # Convert NaN values to None for clean JSON serialization
        df = df.replace({np.nan: None})
        records = df.to_dict(orient="records")
        
        # Load pre-trained metrics JSON
        with open(json_path, "r", encoding="utf-8") as f:
            analytics = json.load(f)
            
        return jsonify({
            "region": region,
            "name": analytics.get("region_name", region.capitalize()),
            "description": REGIONAL_DESCRIPTIONS.get(region, "Thermal GIS mapping layer."),
            "analytics": analytics,
            "records": records
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/heat-risk")
@cache.cached(query_string=True)
@require_api_key
def get_heat_risk():
    region = request.args.get("region", "mirpur12")

    csv_filename = f"{region}_data_calculated.csv"
    csv_path = os.path.join(BASE_DIR, "field_data", csv_filename)

    json_filename = f"{region}_reg_metrics.json"
    json_path = os.path.join(BASE_DIR, "ml_models", json_filename)

    if not os.path.exists(csv_path):
        return jsonify(
            {"error": f"Data not pre-computed for region: {region}. Run main.py first."}
        ), 400

    try:
        df = pd.read_csv(csv_path)
        records = compute_heat_risk_from_dataframe(df)

        if not records:
            return jsonify(
                {"error": f"No valid LST/NDVI records found for region: {region}."}
            ), 400

        region_name = region.capitalize()
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                analytics = json.load(f)
            region_name = analytics.get("region_name", region_name)

        return jsonify(
            {
                "region": region,
                "name": region_name,
                "description": REGIONAL_DESCRIPTIONS.get(
                    region, "Thermal GIS mapping layer."
                ),
                "records": records,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/predict-temperature")
def predict_temperature():
    region = request.args.get("region", "mirpur12")
    model_name = request.args.get("model")

    try:
        result = predict_temperature_for_region(
            BASE_DIR,
            region=region,
            model_name=model_name,
        )
        result["description"] = REGIONAL_DESCRIPTIONS.get(
            region, "Thermal GIS mapping layer."
        )
        return jsonify(result)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/recommendations")
@cache.cached(query_string=True)
@require_api_key
def get_recommendations():
    region = request.args.get("region", "mirpur12")
    priority_only = request.args.get("priorityOnly", "false").lower() in {"1", "true", "yes"}

    csv_filename = f"{region}_data_calculated.csv"
    csv_path = os.path.join(BASE_DIR, "field_data", csv_filename)

    json_filename = f"{region}_reg_metrics.json"
    json_path = os.path.join(BASE_DIR, "ml_models", json_filename)

    if not os.path.exists(csv_path):
        return jsonify(
            {"error": f"Data not pre-computed for region: {region}. Run main.py first."}
        ), 400

    try:
        df = pd.read_csv(csv_path)
        recommendations, summary = generate_recommendations_from_dataframe(df)

        if not recommendations:
            return jsonify(
                {"error": f"No valid LST/NDVI records found for region: {region}."}
            ), 400

        if priority_only:
            recommendations = [item for item in recommendations if item["priorityArea"]]

        region_name = region.capitalize()
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                analytics = json.load(f)
            region_name = analytics.get("region_name", region_name)

        return jsonify(
            {
                "region": region,
                "name": region_name,
                "description": REGIONAL_DESCRIPTIONS.get(
                    region, "Thermal GIS mapping layer."
                ),
                "summary": summary,
                "recommendations": recommendations,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/climate-score")
@cache.cached(query_string=True)
@require_api_key
def get_climate_score():
    region = request.args.get("region", "mirpur12")

    csv_filename = f"{region}_data_calculated.csv"
    csv_path = os.path.join(BASE_DIR, "field_data", csv_filename)

    json_filename = f"{region}_reg_metrics.json"
    json_path = os.path.join(BASE_DIR, "ml_models", json_filename)

    if not os.path.exists(csv_path):
        return jsonify(
            {"error": f"Data not pre-computed for region: {region}. Run main.py first."}
        ), 400

    try:
        df = pd.read_csv(csv_path)
        result = compute_climate_resilience_from_dataframe(df)

        region_name = region.capitalize()
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                analytics = json.load(f)
            region_name = analytics.get("region_name", region_name)

        return jsonify(
            {
                "region": region,
                "name": region_name,
                "description": REGIONAL_DESCRIPTIONS.get(
                    region, "Thermal GIS mapping layer."
                ),
                **result,
            }
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/alerts")
@cache.cached(query_string=True)
@require_api_key
def get_alerts():
    region = request.args.get("region", "mirpur12")
    include_historical = request.args.get("includeHistorical", "false").lower() in {
        "1",
        "true",
        "yes",
    }

    csv_filename = f"{region}_data_calculated.csv"
    csv_path = os.path.join(BASE_DIR, "field_data", csv_filename)

    json_filename = f"{region}_reg_metrics.json"
    json_path = os.path.join(BASE_DIR, "ml_models", json_filename)

    if not os.path.exists(csv_path):
        return jsonify(
            {"error": f"Data not pre-computed for region: {region}. Run main.py first."}
        ), 400

    try:
        df = pd.read_csv(csv_path)
        result = evaluate_heatwave_alerts(
            BASE_DIR,
            region=region,
            df=df,
            include_historical=include_historical,
        )

        region_name = region.capitalize()
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                analytics = json.load(f)
            region_name = analytics.get("region_name", region_name)

        result["name"] = region_name
        result["description"] = REGIONAL_DESCRIPTIONS.get(
            region, "Thermal GIS mapping layer."
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze-region", methods=["POST"])
def analyze_region():
    region = request.args.get("region") or request.form.get("region", "mirpur12")

    try:
        geojson_document = None

        if request.is_json:
            payload = request.get_json(silent=True) or {}
            region = payload.get("region", region)
            geojson_document = payload.get("geojson")
        elif "geojson" in request.files:
            upload = request.files["geojson"]
            geojson_document = json.load(upload.stream)
        elif "file" in request.files:
            upload = request.files["file"]
            geojson_document = json.load(upload.stream)
        else:
            return jsonify(
                {
                    "error": (
                        "GeoJSON polygon upload required. Send JSON body "
                        "{ region, geojson } or multipart file field 'geojson'."
                    )
                }
            ), 400

        if geojson_document is None:
            return jsonify({"error": "Missing 'geojson' in request body."}), 400

        validation = validate_geojson(geojson_document)
        if not validation.get("valid"):
            return jsonify({"error": validation.get("error", "Invalid GeoJSON.")}), 400

        csv_filename = f"{region}_data_calculated.csv"
        csv_path = os.path.join(BASE_DIR, "field_data", csv_filename)
        json_filename = f"{region}_reg_metrics.json"
        json_path = os.path.join(BASE_DIR, "ml_models", json_filename)

        if not os.path.exists(csv_path):
            return jsonify(
                {"error": f"Data not pre-computed for region: {region}. Run main.py first."}
            ), 400

        df = pd.read_csv(csv_path)
        result = analyze_region_polygon(BASE_DIR, region, geojson_document, df)

        region_name = region.capitalize() if region else "Mirpur12"
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                analytics = json.load(f)
            region_name = analytics.get("region_name", region_name)

        result["name"] = region_name
        result["description"] = REGIONAL_DESCRIPTIONS.get(
            region or "mirpur12", "Thermal GIS mapping layer."
        )
        return jsonify(result)
    except json.JSONDecodeError:
        return jsonify({"error": "Uploaded file is not valid JSON."}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/hotspots")
def get_hotspots():
    sort_by = request.args.get("sortBy", DEFAULT_SORT)
    limit = request.args.get("limit", DEFAULT_LIMIT)

    try:
        result = rank_hotspots(
            BASE_DIR,
            sort_by=sort_by,
            limit=limit,
        )
        return jsonify(result)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/report", methods=["GET", "POST"])
def generate_report():
    regions = request.args.get("regions", "mirpur12")
    export_format = request.args.get("format", DEFAULT_FORMAT)

    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        regions = payload.get("regions", regions)
        export_format = payload.get("format", export_format)
        if isinstance(regions, list):
            regions = ",".join(regions)

    try:
        report_document, exported, export_format = generate_environmental_report(
            BASE_DIR,
            regions=regions,
            export_format=export_format,
            regional_descriptions=REGIONAL_DESCRIPTIONS,
        )

        if export_format == FORMAT_PDF:
            filename = f"{report_document['reportId']}.pdf"
            if isinstance(exported, str):
                exported = exported.encode('utf-8')
            return send_file(
                io.BytesIO(exported),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=filename,
            )

        if export_format == FORMAT_JSON:
            return jsonify(report_document)

        return jsonify({"error": f"Unsupported format: {export_format}"}), 400
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/simulate-green-infrastructure", methods=["GET", "POST"])
def simulate_green_infrastructure_endpoint():
    region = request.args.get("region", "mirpur12")
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    vegetation_increase = request.args.get("vegetationIncrease", 0, type=int)
    tree_count = request.args.get("treeCount", 0, type=int)
    green_roof = request.args.get("greenRoofCoverage", 0, type=int)

    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        region = payload.get("region", region)
        lat = payload.get("lat", lat)
        lng = payload.get("lng", lng)
        vegetation_increase = payload.get("vegetationIncrease", vegetation_increase)
        tree_count = payload.get("treeCount", tree_count)
        green_roof = payload.get("greenRoofCoverage", green_roof)

    try:
        result = simulate_green_infrastructure(
            BASE_DIR,
            region=region,
            vegetation_increase_percent=vegetation_increase,
            tree_plantation_count=tree_count,
            green_roof_coverage=green_roof,
            lat=lat,
            lng=lng,
        )
        result["description"] = REGIONAL_DESCRIPTIONS.get(
            region or "mirpur12", "Thermal GIS mapping layer."
        )
        return jsonify(result)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/simulate-green-growth", methods=["GET", "POST"])
def simulate_green_growth_endpoint():
    region = request.args.get("region", "mirpur12")
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    custom_increase = request.args.get("customIncrease", type=int)
    scenarios = None

    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        region = payload.get("region", region)
        lat = payload.get("lat", lat)
        lng = payload.get("lng", lng)
        custom_increase = payload.get("customIncrease", custom_increase)
        scenarios = payload.get("scenarios")

    try:
        result = simulate_green_growth(
            BASE_DIR,
            region=region,
            scenarios=scenarios,
            lat=lat,
            lng=lng,
            custom_increase=custom_increase,
        )
        result["description"] = REGIONAL_DESCRIPTIONS.get(
            region or "mirpur12", "Thermal GIS mapping layer."
        )
        return jsonify(result)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/climate-analytics")
def climate_analytics():
    try:
        result = build_climate_analytics(BASE_DIR)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/decision-support", methods=["GET", "POST"])
def decision_support():
    regions = request.args.get("regions", request.args.get("region", "mirpur12"))

    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        regions = payload.get("regions", payload.get("region", regions))
        if isinstance(regions, list):
            regions = ",".join(regions)

    try:
        result = generate_decision_support(
            BASE_DIR,
            regions=regions,
            regional_descriptions=REGIONAL_DESCRIPTIONS,
        )
        return jsonify(result)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/hybrid-forecast")
def hybrid_forecast():
    try:
        return jsonify(load_hybrid_forecast(BASE_DIR))
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/model-validation")
def model_validation():
    region = request.args.get("region")
    try:
        return jsonify(load_model_validation(BASE_DIR, region=region))
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/data-provenance")
def data_provenance():
    region = request.args.get("region")
    try:
        return jsonify(load_data_provenance(BASE_DIR, region=region))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gis_maps/graphs/<path:filename>")
def serve_graph_assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, "gis_maps", "graphs"), filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
