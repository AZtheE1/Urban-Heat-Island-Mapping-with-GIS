"""Load thesis-critical ML outputs and data provenance metadata."""

import json
import os

SUPPORTED_REGIONS = ("mirpur12", "dhaka_all", "sylhet", "rajshahi", "chittagong")

HYBRID_METRICS_FILE = "hybrid_reg_metrics.json"
HYBRID_TIMELINE_FILE = "hybrid_projection_timeline.json"

DATA_PROVENANCE = {
    "mirpur12": {
        "region": "mirpur12",
        "name": "Mirpur 12",
        "dataClass": "ground_truth",
        "dataClassLabel": "Ground-truth baseline",
        "pointCount": 20,
        "source": "field_data/mirpur12_ground_data.csv",
        "surveyType": "Field GPS survey with photographic verification",
        "satelliteIntegration": (
            "NDVI and LST computed via surface reflectance presets and "
            "prescribed NDVI/LST formulas fused with ground observations."
        ),
    },
    "dhaka_all": {
        "region": "dhaka_all",
        "name": "Entire Dhaka Metropolitan Area",
        "dataClass": "framework_demo",
        "dataClassLabel": "Scalability demonstration",
        "pointCount": 15,
        "source": "pipeline/preprocessing.py regional presets (seed=42)",
        "surveyType": "Simulated coordinate extension for macro-analysis framework",
        "satelliteIntegration": "Regional thermal profile parameters from divisional presets.",
    },
    "sylhet": {
        "region": "sylhet",
        "name": "Sylhet Division",
        "dataClass": "framework_demo",
        "dataClassLabel": "Scalability demonstration",
        "pointCount": 15,
        "source": "pipeline/preprocessing.py regional presets (seed=42)",
        "surveyType": "Simulated coordinate extension for macro-analysis framework",
        "satelliteIntegration": "Regional thermal profile parameters from divisional presets.",
    },
    "rajshahi": {
        "region": "rajshahi",
        "name": "Rajshahi Division",
        "dataClass": "framework_demo",
        "dataClassLabel": "Scalability demonstration",
        "pointCount": 15,
        "source": "pipeline/preprocessing.py regional presets (seed=42)",
        "surveyType": "Simulated coordinate extension for macro-analysis framework",
        "satelliteIntegration": "Regional thermal profile parameters from divisional presets.",
    },
    "chittagong": {
        "region": "chittagong",
        "name": "Chittagong Division",
        "dataClass": "framework_demo",
        "dataClassLabel": "Scalability demonstration",
        "pointCount": 15,
        "source": "pipeline/preprocessing.py regional presets (seed=42)",
        "surveyType": "Simulated coordinate extension for macro-analysis framework",
        "satelliteIntegration": "Regional thermal profile parameters from divisional presets.",
    },
}

METHODOLOGY_SUMMARY = {
    "ndviFormula": "NDVI = (NIR − Red) / (NIR + Red)",
    "lstFormula": "Predicted Temperature = α − (β × NDVI)",
    "hybridArchitecture": (
        "Hybrid Residual-Fitting: linear macro-temporal trend plus tree-based "
        "residual models (Random Forest, Gradient Boosting, Extra Trees)."
    ),
    "forecastHorizon": "2027–2030 decadal heat-index projections",
    "historicalDataset": "field_data/mirpur_unified_environmental_data.csv (~11k observations, 2020–2026)",
    "fusionNote": (
        "Mirpur 12 integrates field GPS measurements, surface classification, and "
        "derived spectral indices. Divisional regions demonstrate modular framework "
        "scalability using parameterized presets."
    ),
}


def _read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_hybrid_forecast(base_dir):
    """Return hybrid model comparison metrics and 2030 projection timeline."""
    models_dir = os.path.join(base_dir, "ml_models")
    metrics_path = os.path.join(models_dir, HYBRID_METRICS_FILE)
    timeline_path = os.path.join(models_dir, HYBRID_TIMELINE_FILE)

    if not os.path.exists(metrics_path):
        raise FileNotFoundError(
            "Hybrid model metrics not found. Run main.py historical analysis first."
        )

    modelComparison = _read_json(metrics_path)
    timeline = _read_json(timeline_path) if os.path.exists(timeline_path) else []

    observed = [row for row in timeline if row.get("Model") == "Observed Baseline"]
    projections = [row for row in timeline if row.get("Year", 0) >= 2027]

    best_hybrid = None
    for entry in modelComparison:
        if entry.get("Model", "").startswith("Hybrid"):
            if best_hybrid is None or entry.get("R2", 0) > best_hybrid.get("R2", 0):
                best_hybrid = entry

    best_model_name = best_hybrid["Model"] if best_hybrid else "Hybrid Extra Trees"
    best_projections = [
        row for row in projections if row.get("Model") == best_model_name
    ]
    best_projections.sort(key=lambda item: item["Year"])

    return {
        "modelComparison": modelComparison,
        "bestHybridModel": best_model_name,
        "timeline": timeline,
        "observedSeries": observed,
        "projectionSeries": best_projections,
        "projectionHorizon": [2027, 2028, 2029, 2030],
        "methodology": METHODOLOGY_SUMMARY["hybridArchitecture"],
    }


def load_model_validation(base_dir, region=None):
    """Return per-region and aggregate ML validation metrics."""
    models_dir = os.path.join(base_dir, "ml_models")
    regions = [region] if region else list(SUPPORTED_REGIONS)

    regionalMetrics = []
    for region_id in regions:
        if region_id not in SUPPORTED_REGIONS:
            raise ValueError(f"Unsupported region: {region_id}")

        metrics_path = os.path.join(models_dir, f"{region_id}_reg_metrics.json")
        if not os.path.exists(metrics_path):
            continue

        metrics = _read_json(metrics_path)
        provenance = DATA_PROVENANCE.get(region_id, {})
        regionalMetrics.append(
            {
                "region": region_id,
                "name": metrics.get("region_name", region_id),
                "dataClass": provenance.get("dataClass"),
                "dataClassLabel": provenance.get("dataClassLabel"),
                "linearRegression": {
                    "formula": metrics.get("linear_regression", {}).get("formula")
                    or f"Temperature = {metrics.get('alpha_intercept')} - ({metrics.get('beta_slope')} × NDVI)",
                    "r2": metrics.get("r2_score"),
                    "rmse": metrics.get("rmse"),
                    "mae": metrics.get("mae"),
                    "alpha": metrics.get("alpha_intercept"),
                    "beta": metrics.get("beta_slope"),
                },
                "decisionTree": metrics.get("decision_tree"),
                "randomForest": metrics.get("random_forest"),
                "avgTemp": metrics.get("avg_temp"),
                "peakHotspot": metrics.get("peak_hotspot"),
                "peakCoolspot": metrics.get("peak_coolspot"),
            }
        )

    if not regionalMetrics:
        raise FileNotFoundError("No regional ML metrics found. Run main.py first.")

    hybrid_path = os.path.join(models_dir, HYBRID_METRICS_FILE)
    hybridComparison = _read_json(hybrid_path) if os.path.exists(hybrid_path) else []

    return {
        "regions": regionalMetrics,
        "hybridComparison": hybridComparison,
        "summary": {
            "mirpur12R2": next(
                (m["linearRegression"]["r2"] for m in regionalMetrics if m["region"] == "mirpur12"),
                None,
            ),
            "bestHybridModel": max(hybridComparison, key=lambda x: x.get("R2", 0))["Model"]
            if hybridComparison
            else None,
            "bestHybridR2": max((x.get("R2", 0) for x in hybridComparison), default=None),
        },
    }


def load_data_provenance(base_dir, region=None):
    """Return methodology summary and per-region data authenticity matrix."""
    regions = [region] if region else list(SUPPORTED_REGIONS)
    matrix = []
    for region_id in regions:
        if region_id not in DATA_PROVENANCE:
            continue
        entry = dict(DATA_PROVENANCE[region_id])
        csv_path = os.path.join(base_dir, "field_data", f"{region_id}_data_calculated.csv")
        entry["pipelineReady"] = os.path.exists(csv_path)
        matrix.append(entry)

    return {
        "methodology": METHODOLOGY_SUMMARY,
        "regions": matrix,
    }
