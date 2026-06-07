# 🏗️ Project Architecture & Workflow Guide

Welcome to the Urban Heat Island (UHI) Mapping Project! This document serves as the master architectural blueprint for our software pipeline. It explains how our python data pipeline is engineered, how data flows from spatial satellites and ground sensor logs to our analytical modules, and defines the detailed responsibilities for each of our four assigned roles.

---

## 🎯 1. Project Purpose, Inputs & Outputs

**The Purpose:**  
Cities are rapidly heating up because dense concrete infrastructures absorb solar radiation, while natural green canopies and water bodies act as cooling sinks. The core objective of this project is to develop an interactive GIS mapping and predictive environmental analytics system. By analyzing spatial and ground-level telemetry, urban planners can mathematically predict how expanding the green canopy (increasing NDVI) will directly lower localized surface temperatures, aiding in climate-resilient sustainable city planning.

* **📥 Primary Inputs (Data Sources):**  
  - Baseline ground-verification database (`field_data/mirpur12_ground_data.csv`), which includes exact GPS coordinates, temperature measurements, environmental surface types (Concrete, Asphalt, Vegetation), and linked real-world photographic evidence of 20 baseline points.
  - Raw high-resolution coordinates data (`field_data/mirpur_unified_environmental_data.csv`) detailing 11,627 rows of micro-observations.
  - Geographic boundaries and vector coordinate presets (`satellite_data/placeholders.js`) for the 5 selected zones: Mirpur 12, Entire Dhaka metropolitan area, Sylhet division, Rajshahi division, and Chittagong division.
* **💻 Processing Pipeline (The Core Engine):**  
  - A unified Python data pipeline utilizing the **Pandas** and **NumPy** libraries for data preprocessing and fusion, standard calculation modules to compute physical temperature indexes, and the **Scikit-Learn** library to run predictive machine learning models (Linear Regression and advanced AI algorithms) to forecast future regional temperatures.
* **📤 The Output (Visualization & Analysis):**  
  - Standalone dynamic Leaflet.js interactive maps (`gis_maps/{region}_heatmap.html`) displaying thermal hotspots, accompanied by high-end statistical comparison plots (`gis_maps/graphs/`) generated via **Matplotlib** and **Seaborn** comparing temperature variations across concrete vs. vegetated surfaces.
  - Serialized predictions and Trained ML coefficients (`ml_models/{region}_reg_metrics.json`) detailing intercepts, slopes, and error tolerances.

---

## 👥 2. Team Role Worksheets & Guidelines

To prevent Git merge conflicts, the workload is strictly partitioned into four highly focused technical roles. Each member has distinct modules to edit, specific data formats to manage, and strict boundaries.

---

### 📡 Role 1: Data Collection & Data Preprocessing
* **Assigned Members:** Sayed, Nusair
* **Workspace boundaries:**
  - Files to modify:
    - [pipeline/preprocessing.py](file:///Users/punam/Desktop/varsity/3-2/Theory/ESL/Project/pipeline/preprocessing.py) (The pipeline loader function `load_regional_data`)
    - [scripts/preprocess_mirpur_data.py](file:///Users/punam/Desktop/varsity/3-2/Theory/ESL/Project/scripts/preprocess_mirpur_data.py) (Preprocesses raw CSV logs)
  - Target Folders: `field_data/`, `gps_coordinates/`, `satellite_data/`.
  - Strictly Forbidden: Do not edit mathematical calculations, plotting functions, or machine learning models.
* **What to do:**
  1. Load ground CSV files and satellite preset variables.
  2. Implement text cleaning, strip empty characters, ensure proper parsing of timestamps, and remove duplicate entries.
  3. Validate coordinates against regional bounding boxes.
  4. Generate random simulated coordinates for divisional expansions (Dhaka All, Sylhet, Rajshahi, Chittagong) to perform scale-up testing.
* **How to implement:**
  - Open `pipeline/preprocessing.py`. When `load_regional_data` is called with `mirpur12`, load the 20-point ground-truth file from `field_data/mirpur12_ground_data.csv`. Ensure the column mappings fit the shared schema.
  - When called with divisional preset region IDs, simulate 15 coordinates around the region's geographical center using `np.random` (setting `seed(42)` for consistent runs).
  - Open `scripts/preprocess_mirpur_data.py`. Ensure all file paths refer to `field_data/`.

---

### ✍️ Role 2: Calculation & Report Writing
* **Assigned Members:** Punam, Nafiz
* **Workspace boundaries:**
  - Files to modify:
    - [pipeline/calculation.py](file:///Users/punam/Desktop/varsity/3-2/Theory/ESL/Project/pipeline/calculation.py) (Mathematical functions)
    - [scripts/calculate_mirpur_indices.py](file:///Users/punam/Desktop/varsity/3-2/Theory/ESL/Project/scripts/calculate_mirpur_indices.py) (Pre-calculates indices for the high-res dataset)
    - `documentation/` and `documentation/Report writting/` (Academic files)
  - Target Folder: `documentation/`.
  - Strictly Forbidden: Do not modify map popup designs, scatter plot canvas elements, or Scikit-Learn training pipelines.
* **What to do:**
  1. Implement physical formulations for **Normalized Difference Vegetation Index (NDVI)** and **Land Surface Temperature (LST)**.
  2. Provide summary statistical matrices (mean temperature, min/max NDVI, hotspot coordinates, coolspot coordinates).
  3. Author and maintain Chapter 3 (Methodology), Chapter 4 (Results), Chapter 5 (Discussions), and Appendix tables in the final report.
* **How to implement:**
  - Open `pipeline/calculation.py`.
  - Code `compute_ndvi(nir, red)`:
    $$\text{NDVI} = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$$
    Ensure you handle division by zero.
  - Code `perform_mathematical_calculations(df)`:
    If NDVI is already present (e.g. in ground-truth files), synthesize Red and NIR bands to calculate verified indices. Otherwise, estimate Red and NIR based on surface type offsets and weather conditions.
  - Ensure `calculate_mirpur_indices.py` references imports correctly and writes calculated indices to `field_data/mirpur_calculated_environmental_indices.csv`.

---

### 🎨 Role 3: Dataset Plotting & Visualization
* **Assigned Members:** Spondon, Rushafi
* **Workspace boundaries:**
  - Files to modify:
    - [pipeline/plotting.py](file:///Users/punam/Desktop/varsity/3-2/Theory/ESL/Project/pipeline/plotting.py) (specifically static plots and point marker mapping functions)
  - Target Folder: `gis_maps/graphs/` and coordinate point marker layers.
  - Strictly Forbidden: Do not edit regression modeling loops, JSON metrics file generation, or the Folium Heatmap density layer.
* **What to do:**
  1. Render static comparative graphs (Temperature vs. NDVI scatter plots with fitted regression lines, boxplots of surface types, and traffic heat bars) using Matplotlib/Seaborn.
  2. Implement coordinate-based GIS mapping point overlays mapping sensor coordinates, surface type properties, and site photos.
* **How to implement:**
  - Open `pipeline/plotting.py`.
  - In `generate_visualizations()`, save matplotlib scatter plots to `gis_maps/graphs/{region}_concrete_vs_veg_scatter.png`.
  - Configure point markers (`folium.CircleMarker`) in Leaflet to map sensor coordinate locations. Inject popups showing the `Image` (loaded from `images/`) and telemetry values.

---

### 🧠 Role 4: Predictive Analysis (ML)
* **Assigned Members:** Ajwad, Sabbir
* **Workspace boundaries:**
  - Files to modify:
    - [pipeline/prediction.py](file:///Users/punam/Desktop/varsity/3-2/Theory/ESL/Project/pipeline/prediction.py) (ML models)
    - [pipeline/plotting.py](file:///Users/punam/Desktop/varsity/3-2/Theory/ESL/Project/pipeline/plotting.py) (Folium Heatmap density layer generation)
  - Target Folder: `ml_models/` and `gis_maps/{region}_heatmap.html`.
  - Strictly Forbidden: Do not edit static Matplotlib scatter/bar plots or ground-truth coordinate ingestion routines.
* **What to do:**
  1. Train a **Linear Regression** model mapping NDVI to Surface Temperature.
  2. Extract the model's intercept ($\alpha$) and slope coefficient ($\beta$).
  3. Train **Decision Tree** and **Random Forest** regressors to capture nonlinear trends.
  4. Calculate performance tolerances: Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Coefficient of Determination ($R^2$ Score).
  5. Generate Folium interactive **Heatmaps** showing predicted regional heat risk overlays and density maps, saving them directly as HTML overlays.
* **How to implement:**
  - Open `pipeline/prediction.py`. Fit Scikit-Learn regression classes and extract coefficients to write to `ml_models/{region}_reg_metrics.json`.
  - Open `pipeline/plotting.py`. Generate the density Heatmap (`folium.plugins.HeatMap`) on predicted coordinates and LST values, exporting it to `gis_maps/{region}_heatmap.html`.

---

## 🗺️ 3. Rearranged File Architecture Layout

The codebase has been restructured into the following directory tree:

```text
Urban-Heat-Island-Mapping-with-GIS/
│
├── README.md                           # Master instructions, stack overview, and role guide
├── main.py                             # Master entry-point running the entire pipeline sequentially
├── project-4.md                        # Official project description and guidelines
│
├── field_data/                         # 🌍 CENTRAL DATA REPOSITORY
│   ├── mirpur12_ground_data.csv        # Ground-truth CSV database (20 points with photos)
│   ├── mirpur_unified_environmental_data.csv       # Raw high-resolution dataset
│   ├── mirpur_unified_environmental_data_clean.csv # Cleaned high-resolution dataset
│   ├── mirpur_calculated_environmental_indices.csv # Calculated high-resolution dataset
│   ├── mirpur_ml_ready_data_clean.csv  # Preprocessed & encoded ML-ready dataset
│   ├── mirpur_encoding_dictionary_clean.csv # Category encoding map dictionary
│   ├── mirpur_preprocessing_report.md  # Generated preprocessing analysis report
│   ├── mirpur_historical_temperatures.csv # Historical daily temperature logs
│   └── {region}_data_calculated.csv    # Pipeline-calculated regional datasets for the dashboard
│
├── gps_coordinates/                    # 📍 FIELD GPS COORDINATES
│   └── mirpur12_gps_coordinates.csv    # GPS-tagged field coordinate records
│
├── satellite_data/                     # 🛰️ REMOTE SENSING PRESETS
│   ├── placeholders.js                 # Regional bounding vectors and city coordinate presets
│   └── templates/                      # Data ingestion templates for field, history, and satellite
│
├── gis_maps/                           # 🎨 VISUALIZATIONS & SPATIAL LAYERS
│   ├── {region}_heatmap.html           # Standalone Folium Leaflet.js interactive maps
│   └── graphs/
│       └── {region}_concrete_vs_veg_scatter.png # Comparative scatter plots of LST vs NDVI
│
├── ml_models/                          # 🧠 MACHINE LEARNING METRICS
│   └── {region}_reg_metrics.json       # Serialized AI model accuracies, formulas, and parameters
│
├── pipeline/                           # ⚙️ PYTHON PIPELINE LOGIC MODULES
│   ├── __init__.py                     # Package initialization and function exports
│   ├── preprocessing.py                # Ingestion & cleaning
│   ├── calculation.py                  # NDVI & LST calculations
│   ├── heat_risk.py                    # Heat Risk Index (HRI) composite scoring
│   ├── temperature_prediction/         # Modular future temperature forecasting
│   ├── recommendations/                # Tree plantation recommendation engine
│   ├── climate_resilience/             # Climate resilience scoring (0-100)
│   ├── heatwave_alerts/                # Heatwave alert monitoring engine
│   ├── geo_analytics/                  # GeoJSON polygon spatial analytics
│   ├── hotspot_ranking/                # Cross-region hotspot ranking engine
│   ├── report_generator/               # Automated environmental report exports
│   ├── green_simulation/               # Green infrastructure NDVI growth simulation
│   ├── edss/                           # Environmental Decision Support System
│   ├── plotting.py                     # Heatmaps & comparative plots
│   └── prediction.py                   # Machine Learning regressor models
│
├── backend/                            # 💻 FLASK WEB APP BACKEND
│   ├── app.py                          # Routing and API endpoints (/api/heat-data, /api/heat-risk)
│   └── models/                         # Reserved for backend analytics helpers
│
├── frontend/                           # 🌐 INTERACTIVE DASHBOARD FRONTEND
│   ├── index.html                      # Glassmorphic web layout
│   ├── css/
│   │   └── styles.css                  # Styling guidelines
│   ├── js/
│   │   └── app.js                      # Frontend dashboard controller
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
    ├── project_architecture.md         # THIS FILE: Master architectural guide
    ├── regional_summaries_report.md    # Geographic explanations for divisional profiles
    └── Report writting/
        └── ESL Group 4 Report.md      # Flawless academic report containing all thesis chapters
```

---

## 📐 4. Mathematical Formulations & Data Flow

Here is how data flows sequentially through our Python pipeline:

```mermaid
graph TD
    %% Define Styles
    classDef data fill:#2b3a42,stroke:#4a90e2,stroke-width:2px,color:#fff;
    classDef pre fill:#1a252c,stroke:#e67e22,stroke-width:2px,color:#fff;
    classDef math fill:#34495e,stroke:#9b59b6,stroke-width:2px,color:#fff;
    classDef plot fill:#2c3e50,stroke:#2ecc71,stroke-width:2px,color:#fff;
    classDef ml fill:#22313f,stroke:#f1c40f,stroke-width:2px,color:#fff;

    %% Data Sources
    subgraph Data Layer (Inputs)
        A[field_data/mirpur12_ground_data.csv]:::data
        B[satellite_data/placeholders.js]:::data
    end

    %% Preprocessing
    subgraph Role 1 Module
        C[pipeline/preprocessing.py<br>Ingestion & Cleaning]:::pre
    end

    %% Calculations
    subgraph Role 2 Module
        D[pipeline/calculation.py<br>LST & NDVI Computations]:::math
    end

    %% Visualization
    subgraph Role 3 Module
        E[pipeline/plotting.py<br>Matplotlib Graphs & GIS Point Markers]:::plot
    end

    %% Prediction
    subgraph Role 4 Module
        F[pipeline/prediction.py & plotting.py<br>ML Models & Folium Heatmaps]:::ml
    end

    %% Connections
    A --> C
    B --> C
    C -->|Unified DataFrame Contract| D
    D -->|Calculated DataFrame| E
    D -->|Calculated DataFrame| F
    E -->|Generates HTML/PNG Visuals| G[gis_maps/ Directory]:::data
    F -->|Generates Accuracy Logs| H[ml_models/ Directory]:::data
    D -->|Calculated Data CSV| I[field_data/ Directory]:::data
```

### 🔄 Pipeline Execution Steps:
1. **Trigger**: Run `python main.py`.
2. **Preprocess (Role 1)**: Reads `mirpur12_ground_data.csv` and presets.
3. **Calculate (Role 2)**: Computes indices, sets `Temperature = LST_C`, and saves data outputs to `field_data/{region}_data_calculated.csv`.
4. **Plot (Role 3)**: Generates static scatter plots under `gis_maps/graphs/` and Leaflet point markers.
5. **Predict & Heatmap (Role 4)**: Trains ML models, outputs Intercept ($\alpha$) and Slope ($\beta$), writes metrics to `ml_models/{region}_reg_metrics.json`, and generates Folium density Heatmaps under `gis_maps/`.
6. **Serve**: Start Flask backend `python dashboard/run_dashboard.py`. The backend serves the dashboard webpage and reads preprocessed CSVs and JSON files directly, ensuring the UI remains fast and perfectly aligned with pipeline parameters. Eight JSON API endpoints are available:
   - `GET /api/heat-data?region={id}` — full regional records and ML analytics
   - `GET /api/heat-risk?region={id}` — per-location Heat Risk Index scores (`pipeline/heat_risk.py`)
   - `GET /api/predict-temperature?region={id}` — regression-based 1/3/5-year forecasts (`pipeline/temperature_prediction/`)
   - `GET /api/recommendations?region={id}` — tree plantation and green-infrastructure plans (`pipeline/recommendations/`)
   - `GET /api/climate-score?region={id}` — climate resilience score with breakdown (`pipeline/climate_resilience/`)
   - `GET /api/alerts?region={id}` — heatwave threshold alerts (`pipeline/heatwave_alerts/`)
   - `POST /api/analyze-region` — GeoJSON polygon area statistics (`pipeline/geo_analytics/`)
   - `GET /api/hotspots` — cross-region top-10 hotspot ranking (`pipeline/hotspot_ranking/`)
   - `GET|POST /api/report` — automated environmental reports in JSON or PDF (`pipeline/report_generator/`)
   - `GET|POST /api/simulate-green-growth` — vegetation growth cooling simulation (`pipeline/green_simulation/`)
   - `GET|POST /api/decision-support` — EDSS policy recommendations (`pipeline/edss/`)
   - `GET /api/hybrid-forecast` — hybrid ML model comparison and 2027–2030 projection timeline (`pipeline/thesis_analytics/`)
   - `GET /api/model-validation` — regional R²/RMSE/MAE and hybrid model metrics (`pipeline/thesis_analytics/`)
   - `GET /api/data-provenance` — ground-truth vs framework-demo data classification (`pipeline/thesis_analytics/`)
