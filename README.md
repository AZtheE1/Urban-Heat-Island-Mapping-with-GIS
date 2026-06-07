# 🌡️ Urban Heat Island Mapping & Predictive GIS Analytics System

Welcome to the **Urban Heat Island (UHI) Mapping & Analytics System**. This repository serves as a modular, high-end collaborative codebase designed for **Theory Project Group 4 (CSE 3-2)**.

The system focuses on a high-resolution micro-analysis of **Mirpur 12** as the baseline ground-truth deployment and scales dynamically to divisional boundaries across Bangladesh: **Entire Dhaka Metropolitan Area**, **Sylhet**, **Rajshahi**, and **Chittagong**. It fuses satellite remote sensing data (specifically Land Surface Temperature and vegetation canopy ratios) with ground-truth sensor parameters to process thermal anomalies, apply machine learning models to predict future temperatures, and support sustainable urban planning. The system processes everything using a unified Python data pipeline and serves an interactive spatial dashboard.

---

## 📂 Rearranged Project Architecture & Directory Layout

To align with the project syllabus requirements (specifically Section 9 of the guidelines), the codebase has been rearranged into the following clean, modular structure:

```text
Urban-Heat-Island-Mapping-with-GIS/
│
├── README.md                           # Master instructions, stack overview, and role guide
├── main.py                             # Master entry-point running the entire pipeline sequentially
├── project-4.md                        # Official project description and guidelines
│
├── field_data/                         # 🌍 CENTRAL DATA REPOSITORY (Role 1 & 2 Workspace)
│   ├── mirpur12_ground_data.csv        # The baseline ground-truth CSV database (20 points with photos)
│   ├── mirpur_unified_environmental_data.csv       # Raw high-resolution dataset (11k rows)
│   ├── mirpur_unified_environmental_data_clean.csv # Cleaned high-resolution dataset
│   ├── mirpur_calculated_environmental_indices.csv # Calculated high-resolution dataset
│   ├── mirpur_ml_ready_data_clean.csv  # Preprocessed & encoded ML-ready dataset
│   ├── mirpur_encoding_dictionary_clean.csv # Category encoding map dictionary
│   ├── mirpur_preprocessing_report.md  # Generated preprocessing analysis report
│   ├── mirpur_historical_temperatures.csv # Historical daily temperature logs
│   └── {region}_data_calculated.csv    # Pipeline-calculated regional datasets for the dashboard
│
├── gps_coordinates/                    # 📍 FIELD GPS COORDINATES (Role 1 Workspace)
│   └── mirpur12_gps_coordinates.csv    # GPS-tagged field coordinate records extracted from survey
│
├── satellite_data/                     # 🛰️ REMOTE SENSING PRESETS (Role 1 & 2 Workspace)
│   ├── placeholders.js                 # Regional bounding vectors and city coordinate presets
│   └── templates/                      # Data ingestion templates for field, history, and satellite
│
├── gis_maps/                           # 🎨 VISUALIZATIONS & SPATIAL LAYERS (Role 3 Workspace)
│   ├── {region}_heatmap.html           # Standalone Folium Leaflet.js interactive maps
│   └── graphs/
│       └── {region}_concrete_vs_veg_scatter.png # Comparative scatter plots of LST vs NDVI
│
├── ml_models/                          # 🧠 MACHINE LEARNING METRICS (Role 4 Workspace)
│   └── {region}_reg_metrics.json       # Serialized AI model accuracies, formulas, and parameters
│
├── pipeline/                           # ⚙️ PYTHON PIPELINE LOGIC MODULES (Collaborative Core)
│   ├── __init__.py                     # Package initialization and function exports
│   ├── preprocessing.py                # Role 1: Ingests, cleans, and merges CSV & satellite datasets
│   ├── calculation.py                  # Role 2: Implements LST & NDVI mathematical calculations
│   ├── heat_risk.py                    # Role 2: Heat Risk Index (HRI) composite scoring
│   ├── temperature_prediction/         # Role 4: Modular future temperature forecasting
│   ├── recommendations/                # Role 2/4: Tree plantation recommendation engine
│   ├── climate_resilience/             # Role 2/4: Climate resilience scoring (0-100)
│   ├── heatwave_alerts/                # Role 4: Heatwave alert monitoring engine
│   ├── geo_analytics/                  # Role 1/2: GeoJSON polygon spatial analytics
│   ├── hotspot_ranking/                # Role 2/4: Cross-region hotspot ranking engine
│   ├── report_generator/               # Role 2/4: Automated environmental report exports
│   ├── green_simulation/               # Role 4: Green infrastructure NDVI growth simulation
│   ├── edss/                           # Role 4: Environmental Decision Support System
│   ├── plotting.py                     # Role 3: Generates Folium heatmaps & Matplotlib graphs
│   └── prediction.py                   # Role 4: Trains AI / ML regressors for heat prediction
│
├── backend/                            # 💻 FLASK WEB APP BACKEND (Backend Integration)
│   ├── app.py                          # Serving index.html and exposing unified regional API
│   └── models/                         # Reserved for backend analytics helpers
│
├── frontend/                           # 🌐 INTERACTIVE DASHBOARD FRONTEND (Frontend Integration)
│   ├── index.html                      # Glassmorphic responsive analytics layout
│   ├── css/
│   │   └── styles.css                  # Custom styling, responsive grids, and animations
│   ├── js/
│   │   └── app.js                      # Leaflet.js map renderer, dynamic tables, and Chart.js integration
│   └── images/
│       └── *.jpeg                      # 20 geotagged site verification photos of Mirpur 12
│
├── dashboard/                          # 🚀 WEB SERVER RUNNER
│   └── run_dashboard.py                # Server launcher script to run the Flask application
│
├── presentation/                       # 📊 SLIDES & PRESENTATION OUTLINES
│   └── presentation_outline.md         # PowerPoint outline and Viva prep guide
│
└── documentation/                      # 📝 DOCUMENTATION & REPORT WRITING
    ├── Heat Map.md                     # LaTeX equations and visualization constraints
    ├── project_architecture.md         # Master architectural workflow document
    ├── regional_summaries_report.md    # Geographic explanations for divisional profiles
    └── Report writting/
        └── ESL Group 4 Report.md      # Flawless academic report containing all thesis chapters
```

---



## 📊 Shared Data Contract (Pipeline Schema)

To maintain flawless coordination across preprocessing, calculation, mapping, and ML modeling, the standardized data dictionary structure returned by the pipeline and served via `/api/heat-data` adheres to this contract:

```json
{
  "region": "mirpur12",
  "name": "Mirpur 12",
  "description": "Hyper-local baseline micro-analysis...",
  "analytics": {
    "alpha_intercept": 30.88,
    "beta_slope": 15.16,
    "avg_temp": 30.86,
    "r2_score": 0.4485,
    "rmse": 5.541,
    "mae": 4.9998,
    "peak_hotspot": {
      "name": "Mirpur-10 Roundabout",
      "temp": 43.991,
      "lat": 23.8248,
      "lng": 90.3621
    },
    "peak_coolspot": {
      "name": "National Botanical Garden",
      "temp": 10.0,
      "lat": 23.827,
      "lng": 90.363
    }
  },
  "records": [
    {
      "LocationID": 1,
      "LocationName": "Mirpur-12 Metrorail station",
      "Latitude": 23.826606,
      "Longitude": 90.364136,
      "Temperature": 32.5,
      "SurfaceType": "Concrete",
      "NDVI": 0.1,
      "TrafficDensity": "High",
      "Time": "Afternoon",
      "Image": "Mirpur-12 Metrorail station, 23.826606, 90.364136, 30-35.jpeg"
    }
  ]
}
```

---

## 🔥 Heat Risk Index API

The `/api/heat-risk` endpoint computes a composite **Heat Risk Index (HRI)** by combining normalized Land Surface Temperature (LST) and NDVI values from pre-calculated regional datasets.

### Formula

```
normalized_lst  = (LST - 10) / (65 - 10)          # clipped to [0, 1]
normalized_ndvi = (NDVI - (-0.3)) / (0.8 - (-0.3)) # clipped to [0, 1]
HRI             = normalized_lst × (1 - normalized_ndvi)
```

### Risk Categories

| HRI Range | Risk Level |
|-----------|------------|
| 0.00 – 0.20 | Very Low |
| 0.20 – 0.40 | Low |
| 0.40 – 0.60 | Moderate |
| 0.60 – 0.80 | High |
| 0.80 – 1.00 | Extreme |

### Request

```
GET /api/heat-risk?region=mirpur12
```

Supported regions: `mirpur12`, `dhaka_all`, `sylhet`, `rajshahi`, `chittagong`

### Response

```json
{
  "region": "mirpur12",
  "name": "Mirpur 12",
  "description": "Hyper-local baseline micro-analysis mapping 20 ground sensor coordinates.",
  "records": [
    {
      "lat": 23.826606,
      "lng": 90.364136,
      "lst": 32.5,
      "ndvi": 0.1,
      "heatRiskIndex": 0.4821,
      "riskLevel": "Moderate"
    }
  ]
}
```

Implementation lives in `pipeline/heat_risk.py` and is served by `backend/app.py`.

---

## 📈 Temperature Prediction API

The `/api/predict-temperature` endpoint trains a regression model on historical annual temperature records and forecasts regional surface temperatures 1, 3, and 5 years ahead.

### Data Sources

1. `field_data/mirpur_historical_temperatures.csv` — daily records aggregated to annual means (primary)
2. `ml_models/{region}_reg_metrics.json` — regional `avg_temp` used as the current baseline

### Request

```
GET /api/predict-temperature?region=mirpur12
GET /api/predict-temperature?region=dhaka_all&model=linear_regression
```

Optional query parameter `model` selects the predictor implementation (default: `linear_regression`).

### Response

```json
{
  "region": "mirpur12",
  "name": "Mirpur 12",
  "description": "Hyper-local baseline micro-analysis mapping 20 ground sensor coordinates.",
  "model": "linear_regression",
  "dataSource": "mirpur_historical_temperatures.csv",
  "baseYear": 2024,
  "currentTemperature": 29.52,
  "predicted1Year": 29.87,
  "predicted3Years": 30.57,
  "predicted5Years": 31.27,
  "evaluation": {
    "rmse": 0.3124,
    "mae": 0.2451,
    "r2": 0.9842
  }
}
```

### Modular Architecture

New models can be added by subclassing `BaseTemperaturePredictor` in `pipeline/temperature_prediction/base.py` and registering them in `pipeline/temperature_prediction/registry.py`:

```python
from pipeline.temperature_prediction.registry import PREDICTOR_REGISTRY
from pipeline.temperature_prediction.base import BaseTemperaturePredictor

class RandomForestTrendPredictor(BaseTemperaturePredictor):
    name = "random_forest"
    ...

PREDICTOR_REGISTRY["random_forest"] = RandomForestTrendPredictor
```

---

## 🌳 Tree Plantation Recommendation API

The `/api/recommendations` endpoint identifies high-temperature, low-NDVI priority areas and returns green-infrastructure intervention plans.

### Scoring

```
vegetationDeficitScore = regional_norm(LST) × (1 - regional_norm(NDVI))
```

Regional min-max normalization is applied within each dataset so intervention tiers reflect relative hotspots inside the selected region.

Priority areas are flagged when LST is above the regional mean and NDVI is below the regional mean, or when the deficit score exceeds 0.45.

### Intervention Levels

| Deficit Score | Intervention Level |
|---------------|-------------------|
| 0.00 – 0.35 | Small intervention |
| 0.35 – 0.60 | Moderate intervention |
| 0.60 – 1.00 | Aggressive intervention |

### Suggested Actions

- **Small intervention** — Tree plantation
- **Moderate intervention** — Tree plantation, Green roofs, Vertical gardens
- **Aggressive intervention** — Tree plantation, Green roofs, Vertical gardens, Community parks

Surface type and traffic density refine the action list per location.

### Request

```
GET /api/recommendations?region=mirpur12
GET /api/recommendations?region=dhaka_all&priorityOnly=true
```

### Response

```json
{
  "region": "mirpur12",
  "name": "Mirpur 12",
  "summary": {
    "totalLocations": 20,
    "priorityAreas": 9,
    "avgVegetationDeficitScore": 0.3124
  },
  "recommendations": [
    {
      "locationName": "Mirpur-12 Metrorail station",
      "lat": 23.826606,
      "lng": 90.364136,
      "lst": 32.5,
      "ndvi": 0.1,
      "surfaceType": "Concrete",
      "vegetationDeficitScore": 0.4821,
      "priorityArea": true,
      "interventionLevel": "Moderate intervention",
      "suggestedActions": [
        "Tree plantation",
        "Green roofs",
        "Vertical gardens"
      ]
    }
  ]
}
```

Implementation lives in `pipeline/recommendations/` and is served by `backend/app.py`.

---

## 🌍 Climate Resilience Score API

The `/api/climate-score` endpoint calculates a composite **Climate Resilience Score (0–100)** from NDVI, average temperature, Heat Risk Index, and green coverage percentage.

### Composite Formula

Each factor contributes **25%** to the final score:

| Factor | Resilience Logic | Component Score |
|--------|------------------|-----------------|
| NDVI | Higher is better | `norm(NDVI) × 100` |
| Average temperature | Lower is better | `(1 - norm(LST)) × 100` |
| Heat Risk Index | Lower is better | `(1 - HRI) × 100` |
| Green coverage % | Higher is better | `greenCoveragePercentage` |

### Categories

| Score Range | Category |
|-------------|----------|
| 0 – 20 | Critical |
| 21 – 40 | Poor |
| 41 – 60 | Moderate |
| 61 – 80 | Good |
| 81 – 100 | Excellent |

### Request

```
GET /api/climate-score?region=mirpur12
```

### Response

```json
{
  "region": "mirpur12",
  "name": "Mirpur 12",
  "climateResilienceScore": 58.42,
  "category": "Moderate",
  "summary": {
    "avgNdvi": 0.4012,
    "avgTemperature": 29.52,
    "avgHeatRiskIndex": 0.1298,
    "greenCoveragePercentage": 42.15,
    "locationCount": 20
  },
  "breakdown": {
    "ndvi": {
      "value": 0.4012,
      "componentScore": 53.75,
      "weight": 0.25,
      "weightedContribution": 13.44
    },
    "averageTemperature": { "value": 29.52, "componentScore": 64.51, "weight": 0.25, "weightedContribution": 16.13 },
    "heatRiskIndex": { "value": 0.1298, "componentScore": 87.02, "weight": 0.25, "weightedContribution": 21.76 },
    "greenCoveragePercentage": { "value": 42.15, "componentScore": 42.15, "weight": 0.25, "weightedContribution": 10.54 }
  },
  "explanation": {
    "summary": "The region is classified as Moderate with a climate resilience score of 58.42/100...",
    "categoryMeaning": "Targeted tree planting and green retrofits can improve resilience within 2-3 planning cycles.",
    "componentNotes": { "ndvi": "...", "averageTemperature": "...", "heatRiskIndex": "...", "greenCoveragePercentage": "..." },
    "strongestFactor": { "component": "heatRiskIndex", "componentScore": 87.02 },
    "weakestFactor": { "component": "greenCoveragePercentage", "componentScore": 42.15 }
  },
  "records": []
}
```

Implementation lives in `pipeline/climate_resilience/` and is served by `backend/app.py`.

---

## 🚨 Heatwave Alert API

The `/api/alerts` endpoint monitors regional temperature readings and triggers heatwave alerts when thresholds are exceeded.

### Alert Thresholds

| Condition | Level |
|-----------|-------|
| > 40°C | Extreme |
| > 38°C | Severe |
| > 35°C | Warning |

### Request

```
GET /api/alerts?region=rajshahi
GET /api/alerts?region=mirpur12&includeHistorical=true
```

Optional `includeHistorical=true` also scans `field_data/mirpur_historical_temperatures.csv` for past heatwave events.

### Response

```json
{
  "region": "rajshahi",
  "name": "Rajshahi",
  "activeAlertCount": 2,
  "highestLevel": "Warning",
  "thresholds": { "warning": 35.0, "severe": 38.0, "extreme": 40.0 },
  "alerts": [
    {
      "level": "Warning",
      "temperature": 36.8,
      "message": "Heatwave Warning: Temperature reached 36.8°C at Rajshahi Site 3. Limit prolonged outdoor exposure, seek shade, and stay hydrated.",
      "timestamp": "2026-06-07T14:30:00Z"
    }
  ]
}
```

### Future SMS / Push Integration

Register custom notifiers by subclassing `BaseAlertNotifier` in `pipeline/heatwave_alerts/notifiers.py`:

```python
from pipeline.heatwave_alerts import evaluate_heatwave_alerts, NotificationDispatcher

class SmsAlertNotifier(BaseAlertNotifier):
    name = "sms"
    def notify(self, alert):
        ...  # integrate Twilio, SNS, etc.

evaluate_heatwave_alerts(..., dispatch_notifications=True, notifiers=[SmsAlertNotifier()])
```

---

## 🗺️ GeoJSON Regional Analytics API

The `/api/analyze-region` endpoint accepts GeoJSON polygon uploads, validates structure, and computes area statistics for observation points inside the polygon.

### Metrics

- Average temperature
- Average NDVI
- Average Heat Risk Index (HRI)
- Point coverage, bounding box, and approximate polygon area (km²)

### Request

JSON body:

```
POST /api/analyze-region
Content-Type: application/json

{
  "region": "mirpur12",
  "geojson": {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[[90.3600, 23.8200], [90.3700, 23.8200], [90.3700, 23.8300], [90.3600, 23.8300], [90.3600, 23.8200]]]
    }
  }
}
```

Multipart upload:

```
POST /api/analyze-region?region=mirpur12
Content-Type: multipart/form-data
geojson=<GeoJSON file>
```

### Response

```json
{
  "region": "mirpur12",
  "name": "Mirpur 12",
  "geojsonValidation": {
    "valid": true,
    "rootType": "Feature",
    "geometryTypes": ["Polygon"],
    "featureCount": 1
  },
  "areaStatistics": {
    "pointCount": 8,
    "totalRegionalPoints": 20,
    "coveragePercentage": 40.0,
    "averageTemperature": 29.87,
    "averageNdvi": 0.42,
    "averageHeatRiskIndex": 0.14,
    "heatRiskLevel": "Very Low",
    "boundingBox": { "minLng": 90.36, "maxLng": 90.37, "minLat": 23.82, "maxLat": 23.83 },
    "approximateAreaSqKm": 1.23,
    "polygonCount": 1
  },
  "points": []
}
```

### Future Shapefile Integration

Geometry sources are pluggable via `BaseGeometryAdapter`. Implement `ShapefileAdapter` in `pipeline/geo_analytics/adapters/shapefile_adapter.py` when geopandas/fiona are added.

---

## 🔥 Hotspot Ranking API

The `/api/hotspots` endpoint ranks observation points across all five analyzed regions and returns the top 10 hottest locations.

### Sorting

| `sortBy` value | Primary sort | Secondary sort |
|----------------|--------------|----------------|
| `temperature` (default) | Highest LST | Highest HRI |
| `heatRiskIndex` | Highest HRI | Highest LST |

### Request

```
GET /api/hotspots
GET /api/hotspots?sortBy=heatRiskIndex
GET /api/hotspots?sortBy=temperature&limit=10
```

### Response

```json
{
  "sortBy": "temperature",
  "limit": 10,
  "totalLocationsAnalyzed": 85,
  "regionsAnalyzed": 5,
  "regionRankings": [
    {
      "region": "rajshahi",
      "regionName": "Rajshahi",
      "locationCount": 15,
      "averageTemperature": 32.97,
      "averageHeatRiskIndex": 0.21,
      "temperatureRank": 1,
      "heatRiskRank": 1
    }
  ],
  "hotspots": [
    {
      "rank": 1,
      "region": "mirpur12",
      "regionName": "Mirpur 12",
      "locationName": "Mirpur-12 Metrorail station",
      "lat": 23.826606,
      "lng": 90.364136,
      "temperature": 32.5,
      "ndvi": 0.1,
      "heatRiskIndex": 0.4821,
      "riskLevel": "Moderate"
    }
  ]
}
```

Implementation lives in `pipeline/hotspot_ranking/` and is served by `backend/app.py`.

---

## 📄 Environmental Report API

The `/api/report` endpoint generates automated environmental reports for selected regions with JSON or PDF export.

### Included Sections (per region)

- Temperature statistics (min, max, mean, median, std)
- NDVI statistics
- Heat Risk Index summary and top hotspots
- Climate resilience score with breakdown
- Green-infrastructure recommendations

### Request

```
GET /api/report?regions=mirpur12&format=json
GET /api/report?regions=mirpur12,dhaka_all&format=pdf
POST /api/report
Content-Type: application/json

{
  "regions": ["mirpur12", "sylhet"],
  "format": "json"
}
```

### JSON Response (excerpt)

```json
{
  "reportId": "env-report-mirpur12-20260607143000",
  "title": "Urban Heat Island Environmental Report",
  "generatedAt": "2026-06-07T14:30:00Z",
  "regions": ["mirpur12"],
  "sections": [
    {
      "region": "mirpur12",
      "name": "Mirpur 12",
      "temperatureStatistics": { "min": 26.5, "max": 32.5, "mean": 29.52, "median": 29.5, "std": 1.8, "count": 20 },
      "ndviStatistics": { "min": 0.1, "max": 0.8, "mean": 0.4, "median": 0.4, "std": 0.2, "count": 20 },
      "heatRiskIndex": { "average": 0.13, "riskLevelDistribution": { "Very Low": 18, "Low": 2 } },
      "climateScore": { "score": 68.1, "category": "Good" },
      "recommendations": { "summary": { "priorityAreas": 8 }, "items": [] }
    }
  ]
}
```

PDF requests return a downloadable `application/pdf` file.

### Extending Export Formats

Add new exporters by subclassing `BaseReportExporter` in `pipeline/report_generator/exporters/` and registering them in `exporters/__init__.py`.

---

## 🌿 Green Infrastructure Simulation API

The `/api/simulate-green-growth` endpoint models hypothetical vegetation increases and estimates resulting temperature reductions using the regional linear regression model.

### Regression Model

```
estimatedTemperature = alpha - (beta × simulatedNDVI)
reduction = currentTemperature - estimatedTemperature
simulatedNDVI = currentNDVI × (1 + vegetationIncreasePercent / 100)
```

Default scenarios: **+10%**, **+20%**, **+30%** vegetation (NDVI increase).

### Request

```
GET /api/simulate-green-growth?region=mirpur12
GET /api/simulate-green-growth?region=mirpur12&lat=23.826606&lng=90.364136
GET /api/simulate-green-growth?region=mirpur12&customIncrease=15

POST /api/simulate-green-growth
{
  "region": "mirpur12",
  "scenarios": [10, 20, 30]
}
```

### Response

```json
{
  "region": "mirpur12",
  "name": "Mirpur 12",
  "model": "linear_regression",
  "formula": "Temperature = 32.41 - (6.95 * NDVI)",
  "baseline": {
    "currentTemperature": 29.52,
    "currentNDVI": 0.4012
  },
  "scenarios": [
    {
      "vegetationIncreasePercent": 10,
      "currentTemperature": 29.52,
      "currentNDVI": 0.4012,
      "simulatedNDVI": 0.4413,
      "estimatedTemperature": 29.24,
      "reduction": 0.28
    }
  ]
}
```

Implementation lives in `pipeline/green_simulation/` and is served by `backend/app.py`.

---

## 🏛️ Environmental Decision Support System (EDSS)

The `/api/decision-support` endpoint aggregates environmental intelligence and returns ranked policy suggestions for urban planners.

### Aggregated Metrics

- **LST** — land surface temperature statistics
- **NDVI** — vegetation index statistics
- **Heat Risk Index** — composite exposure with hotspot distribution
- **Climate Score** — resilience score and category
- **Recommendations** — priority areas and intervention items

### Policy Suggestions

| Policy | Example trigger |
|--------|-----------------|
| Increase tree coverage | Low NDVI, many priority heat areas |
| Create pocket parks | High vegetation deficit zones |
| Deploy cool pavements | High LST on built-up surfaces |
| Install rooftop gardens | Elevated heat risk, moderate resilience |

### Priority Levels

**Critical** · **High** · **Medium** · **Low** (ranked by urgency score)

### Request

```
GET /api/decision-support?region=mirpur12
GET /api/decision-support?regions=mirpur12,rajshahi

POST /api/decision-support
{ "regions": ["mirpur12", "dhaka_all"] }
```

### Response (excerpt)

```json
{
  "system": "Environmental Decision Support System",
  "region": "mirpur12",
  "aggregatedMetrics": {
    "lst": { "mean": 29.52, "max": 32.5, "unit": "C" },
    "ndvi": { "mean": 0.415 },
    "heatRiskIndex": { "average": 0.13 },
    "climateScore": { "score": 68.1, "category": "Good" },
    "recommendations": { "summary": { "priorityAreas": 8 } }
  },
  "policySuggestions": [
    {
      "id": "increase_tree_coverage",
      "title": "Increase tree coverage",
      "priority": "High",
      "rationale": "Average NDVI is 0.415 with 8 priority heat-exposure areas...",
      "machineReadable": { "policyId": "increase_tree_coverage", "priority": "High", "urgencyScore": 55.0 }
    }
  ],
  "humanReadableRecommendations": {
    "executiveSummary": "Mirpur 12 requires high-priority intervention...",
    "priorityActions": ["[High] Increase tree coverage: ..."],
    "fullNarrative": "Environmental Decision Support analysis for Mirpur 12:..."
  }
}
```

### Architecture

```
pipeline/edss/
  domain/           # Policy catalog, priority rules
  infrastructure/ # Data gateway (existing pipeline modules)
  application/      # Policy engine, presenter, service
```

---

## 🎓 Thesis-Critical APIs (Defense Demo)

These endpoints support thesis Objective 3 (forecasting), model validation, and transparent data classification:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/predict-temperature?region=` | 1/3/5-year regional temperature forecast (linear regression on historical series) |
| `GET /api/hybrid-forecast` | Hybrid ML model comparison + 2027–2030 heat-index projection timeline |
| `GET /api/model-validation?region=` | Per-region R², RMSE, MAE, Decision Tree & Random Forest scores |
| `GET /api/data-provenance?region=` | Ground-truth vs framework-demo classification and fusion methodology |

**Ground verification photos:** Run once before demo if images are missing:

```bash
python scripts/generate_ground_verification_images.py
```

See [documentation/demo_rehearsal_script.md](documentation/demo_rehearsal_script.md) for the full 10-minute defense walkthrough.

---

## 🏃 Quick-Start Development Guide

Follow these steps to execute the pipeline and run the dashboard locally:

### 1. Install Dependencies
```bash
pip install pandas numpy matplotlib seaborn folium scikit-learn flask plotly statsmodels --break-system-packages
```

### 2. Execute Data Preprocessing & Mathematical Calculations
Run the standalone data cleaning and calculation scripts:
```bash
python scripts/preprocess_mirpur_data.py
python scripts/calculate_mirpur_indices.py
```
*(This cleans the high-resolution 11k dataset and generates reports under `field_data/`)*.

### 3. Run the Unified Master Pipeline
Execute the master orchestration script from the root directory:
```bash
python main.py
```
*(This processes all 5 regional models, generating Leaflet maps under `gis_maps/`. It then successfully executes the **Historical Longitudinal Analysis**—generating macro-temporal heat matrices, Plotly wind-cooling mechanics, and Hybrid Machine Learning projections [up to 2030] into `gis_maps/graphs/` and `ml_models/`)*.

### 4. Generate ground verification images (thesis demo)
```bash
python scripts/generate_ground_verification_images.py
```

### 5. Launch the Web Dashboard
Start the Flask web server:
```bash
python dashboard/run_dashboard.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser to view the interactive glassmorphic GIS mapping dashboard.
