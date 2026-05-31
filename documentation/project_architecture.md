# 🏗️ Project Architecture & Workflow Guide

Welcome to the Urban Heat Island (UHI) Mapping Project! This document serves as the master architectural blueprint for our software pipeline. It explains how our pure Python data pipeline is engineered, how data flows from spatial satellites and ground sensor logs to our analytical modules, and defines the detailed responsibilities for each of our four assigned roles.

---

## 🎯 1. Project Purpose, Inputs & Outputs

**The Purpose:**  
Cities are rapidly heating up because dense concrete infrastructures absorb solar radiation, while natural green canopies and water bodies act as cooling sinks. The core objective of this project is to develop a pure Python-based environmental mapping and predictive GIS analytics system. By analyzing spatial and ground-level telemetry, urban planners can mathematically predict how expanding the green canopy (increasing NDVI) will directly lower localized surface temperatures, aiding in climate-resilient sustainable city planning.

* **📥 Primary Inputs (Data Sources):**  
  * Satellite rasters (Landsat 8/9 and Sentinel-2) detailing Land Surface Temperature (LST) and Normalized Difference Vegetation Index (NDVI) bands.
  * Our synthesized, high-fidelity ground-verification database (`mirpur12_ground_data.csv`), which includes exact GPS coordinates, temperature measurements, environmental surface types (Concrete, Asphalt, Vegetation), and linked real-world photographic evidence.
* **💻 Processing Pipeline (The Core Engine):**  
  * A unified Python data pipeline utilizing the **Pandas** and **NumPy** libraries for data preprocessing and fusion, standard calculation modules to compute physical temperature indexes, and the **Scikit-Learn** library to run predictive machine learning models (Linear Regression and advanced AI algorithms) to forecast future regional temperatures.
* **📤 The Output (Visualization & Analysis):**  
  * Highly interactive GIS heatmaps generated via the **Folium** library (outputting standalone dynamic `.html` overlays) showing thermal hotspots, accompanied by high-end statistical comparison plots generated via **Matplotlib**, **Seaborn**, and **Plotly** comparing temperature variations across concrete vs. vegetated surfaces.

---

## 👥 2. Role Assignments & Technical Workflows

To ensure our project scales properly without causing Git merge conflicts, the workload is strictly partitioned into four highly focused technical roles. Each member has distinct modules to edit, specific data formats to manage, and strict deliverables to meet.

### 📡 Role 1: Data Collection & Data Preprocessing
* **Assigned Members:** Sayed, Nusair
* **Primary Directive & Workflow:**  
  You are the foundational data provider for the entire analytical stack. Your primary responsibility is to harvest raw satellite imagery from platforms like USGS Earth Explorer and Google Earth Engine (specifically Landsat 8/9 thermal bands and Sentinel-2 optical bands) alongside ground-truth GPS coordinates. You will build the initial ingestion and preprocessing scripts to clean, align, and fuse raw satellite LST/NDVI readings with the ground sensor logs.
* **File Access & Boundaries:**  
  You operate primarily within the `data/` folder and `pipeline/preprocessing.py`. You do not touch the calculation formulas or the ML predictive training models; your strict boundary is spatial data preparation, cleanup, and file fusion.
* **Technical Execution:**  
  You will read ground-truth data from `mirpur12_ground_data.csv` and satellite readings, perform coordinate matching, handle missing values, and merge the datasets into a single, clean Pandas DataFrame. This DataFrame is passed down the pipeline as a standardized data dictionary contract.
* **Deliverables & Final Output:**  
  Clean, preprocessed datasets for Mirpur 12, Dhaka Metropolitan Area, Sylhet, Rajshahi, and Chittagong. You will provide a data preparation summary to the documentation team for inclusion in the final report.

---

### ✍️ Role 2: Calculation & Report Writing
* **Assigned Members:** Punam, Nafiz
* **Primary Directive & Workflow:**  
  You represent the core mathematical engine and academic backbone of the team. Your job is to implement and validate the physical calculations (NDVI and LST) within the Python data pipeline. In addition, you serve as the chief technical writers, organizing and assembling our final academic thesis chapters.
* **File Access & Boundaries:**  
  You operate inside `pipeline/calculation.py`, the `documentation/` directory, and `Report writting/`. You work closely with Role 1 to ingest clean dataframes and output calculated thermal metrics to the visualization and ML modules.
* **Technical Execution:**  
  You will write python functions implementing the mathematical models:
  * **Normalized Difference Vegetation Index (NDVI)**:  
    $$\text{NDVI} = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$$
  * **Land Surface Temperature (LST)**:  
    $$\text{Predicted Temperature} = \alpha - (\beta \times \text{NDVI})$$
  You are responsible for confirming that the calculation outputs line up with physical urban climate models.
* **Deliverables & Final Output:**  
  Highly optimized mathematical calculation scripts (`calculation.py`) and a flawlessly formatted academic report (`ESL Group 4 Report.md`) containing all thesis chapters and Viva preparation documents.

---

### 🎨 Role 3: Dataset Plotting & Visualization
* **Assigned Members:** Spondon, Rushafi
* **Primary Directive & Workflow:**  
  You are responsible for the entire visual and spatial output of the project. Your job is to translate the raw numeric datasets and calculation results into intuitive, interactive GIS heatmaps and comparison graphs that are immediately understandable to urban planning stakeholders.
* **File Access & Boundaries:**  
  You operate exclusively within `pipeline/plotting.py` and the generated visual outputs inside `output/maps/` and `output/graphs/`. You do not edit the ML modeling algorithms or raw database CSVs.
* **Technical Execution:**  
  You will use the **Folium** library to generate standalone dynamic GIS heatmaps. You will configure markers for coordinate points, custom HTML popups mapping physical locations to temperature/image tags, and save them as `.html` files. Additionally, you will build plotting scripts using **Matplotlib** and **Seaborn** to generate scatter plots, bar charts, and temperature distribution graphs comparing concrete vs. vegetation zones.
* **Deliverables & Final Output:**  
  A suite of dynamic Folium maps (e.g. `mirpur12_heatmap.html`) and PNG comparison plots illustrating spatial thermal gradients.

---

### 🧠 Role 4: Predictive Analysis (ML)
* **Assigned Members:** Ajwad, Sabbir
* **Primary Directive & Workflow:**  
  You are responsible for the predictive capabilities of the environmental engine. Your job is to build, train, and validate a series of different machine learning models to forecast future localized temperatures based on vegetation changes and spatial parameters.
* **File Access & Boundaries:**  
  You have sole dominion over `pipeline/prediction.py` and saved model parameter configurations inside `output/models/`. You are strictly forbidden from editing database preprocessing or plotting modules.
* **Technical Execution:**  
  Using the Scikit-Learn library, you will build and fit a Linear Regression model mapping LST vs. NDVI, extracting the intercept ($\alpha$) and cooling slope coefficient ($\beta$). You will also implement advanced machine learning models (such as Random Forest or XGBoost regression) to perform nonlinear predictions. You will compute all performance metrics, including Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and the Coefficient of Determination ($R^2$ Score), exporting them as serialized JSON metrics.
* **Deliverables & Final Output:**  
  A predictive regression engine (`prediction.py`) and accuracy logs verifying that our machine learning predictions fit historical and spatial thermal realities.

---

## 🗺️ 3. System Architecture & Workflow Diagrams

Here is how data flows sequentially through our pure Python pipeline:

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
        A[Satellite Rasters LST/NDVI]:::data
        B[Ground CSV Database mirpur12_ground_data.csv]:::data
    end

    %% Preprocessing
    subgraph Role 1 Module
        C[pipeline/preprocessing.py<br>Ingestion & Fusion]:::pre
    end

    %% Calculations
    subgraph Role 2 Module
        D[pipeline/calculation.py<br>LST & NDVI Computations]:::math
    end

    %% Visualization
    subgraph Role 3 Module
        E[pipeline/plotting.py<br>Folium GIS Maps & Matplotlib Plots]:::plot
    end

    %% Prediction
    subgraph Role 4 Module
        F[pipeline/prediction.py<br>Regression & Machine Learning]:::ml
    end

    %% Connections
    A --> C
    B --> C
    C -->|Unified DataFrame Contract| D
    D -->|Calculated Metrics DataFrame| E
    D -->|Calculated Metrics DataFrame| F
    E -->|Generates HTML/PNG Visuals| G[output/ Directory]:::data
    F -->|Generates Accuracy Logs| G
```

### 🔄 The Step-by-Step Python Pipeline execution:
1. **The Trigger:** The user runs the master script `python main.py`.
2. **Data Ingestion (Role 1):** The preprocessing script reads `mirpur12_ground_data.csv` and merges it with satellite spatial layers.
3. **Core Computation (Role 2):** The calculation module parses the data, validating NDVI and LST variables using mathematical formulas.
4. **Visual Generation (Role 3):** The plotting module generates interactive Folium GIS HTML maps centered over Mirpur 12 and saves them alongside Matplotlib scatter plots comparing surfaces.
5. **AI Modeling (Role 4):** The machine learning module trains linear and nonlinear regression models, evaluates predictive accuracy metrics, and saves accuracy metrics to a JSON configuration.

---

## 📂 4. Project Structure & File Architecture

Our repository is physically organized inside this strict modular hierarchy, ensuring that our development roles operate in separate logical workspaces:

```text
Urban-Heat-Island-Mapping-with-GIS/
│
├── README.md                           # Master instructions, stack overview, and setup guide
│
├── main.py                             # Master entry-point running the entire pipeline sequentially
│
├── documentation/                      # 📝 ROLE 2'S WORKSPACE (Technical Writing)
│   ├── Heat Map.md                     # Technical constraints, workflow, and LaTeX formulas
│   ├── project_architecture.md         # THIS FILE: Pure Python workflow and role architecture
│   └── regional_summaries_report.md    # Theoretical breakdown of regional thermal profiles
│
├── data/                               # 🌍 CENTRAL DATA REPOSITORY (Role 1 Database)
│   ├── environmental/
│   │   └── mirpur12_ground_data.csv    # The ground-truth CSV database (temps, coords, and images)
│   ├── geojson/
│   │   └── placeholders.js             # Regional bounding vectors and city coordinates presets
│   └── mirpur 12 area ss/              # Geographic screenshots and satellite map overlays
│
├── pipeline/                           # ⚙️ PYTHON PIPELINE LOGIC MODULES (Role Workspaces)
│   ├── __init__.py                     # Module package initializer
│   ├── preprocessing.py                # Role 1: Ingests, cleans, and merges CSV & satellite datasets
│   ├── calculation.py                  # Role 2: Implements LST & NDVI mathematical calculations
│   ├── plotting.py                     # Role 3: Generates Folium interactive heatmaps & Matplotlib graphs
│   └── prediction.py                   # Role 4: Trains AI / Machine Learning models for heat prediction
│
└── output/                             # 📊 GENERATED PIPELINE OUTPUTS & VISUALIZATIONS (Outputs)
    ├── maps/
    │   └── {region}_heatmap.html       # Dynamic Folium GIS HTML maps with popups
    ├── graphs/
    │   └── {region}_concrete_vs_veg_scatter.png # Comparative scatter plots of LST vs NDVI
    └── models/
        └── {region}_reg_metrics.json   # Serialized AI model accuracies & metrics (MAE, RMSE, R2)
```
