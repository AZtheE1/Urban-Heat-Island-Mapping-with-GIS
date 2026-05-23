# Urban-Heat-Island-Mapping-with-GIS
An interactive GIS mapping and predictive analytics dashboard tracking the Urban Heat Island (UHI) effect—anchored on a micro-analysis of Mirpur 12 and scalable to major divisions across Bangladesh. Built with Leaflet.js and Python.


It is an interactive, data-driven environmental management application designed to visualize, analyze, and predict the Urban Heat Island (UHI) effect. This project features a high-resolution micro-analysis of the **Mirpur 12** area in Dhaka City as its baseline deployment, with a scalable regional architecture extended to the **Entire Dhaka Metropolitan Area, Sylhet, Rajshahi, and Chittagong**.

## 📌 Project Overview
Urban Heat Islands occur when dense cities trap heat due to concrete infrastructures, asphalt surfaces, and a lack of green vegetation. This system fuses satellite remote sensing data (Land Surface Temperature and NDVI) with simulated ground-truth parameters to map out high-risk thermal zones, helping municipal authorities support sustainable urban planning.

### 🌟 Key Features
* **Hyper-Local & Macro Scaling:** Toggle seamlessly between a deep-dive analysis of Mirpur 12 and divisional-level thermal profiles across Bangladesh.
* **Interactive GIS Dashboard:** Real-time spatial visualization powered by Leaflet.js with dynamic thermal heat map overlays.
* **Algorithmic Heat Prediction:** A lightweight, optimized regression engine that evaluates the inverse correlation between vegetation density (NDVI) and heat retention.
* **Comparative Analytics:** Dynamic charting that cross-examines temperatures across various urban zones (e.g., Concrete Main Roads vs. Vegetated Parks).

---

## 🛠️ Tech Stack & Architecture

### System Data Flow
[Satellite Data: Landsat 8/9 & Sentinel-2] ──┐
├──► [Python Backend API] ──► [Leaflet.js Dashboard UI]
[Synthesized Coordinate Ground Datasets] ───┘

* **Frontend:** HTML5, CSS3, Bootstrap, JavaScript (ES6)
* **Interactive Maps:** Leaflet.js (`Leaflet.heat` plugin)
* **Backend:** Python (Flask / Django)
* **Data Processing & Modeling:** QGIS, Pandas, Scikit-Learn
* **Charts & Visualizations:** Chart.js / Plotly

---

## 📁 Repository Structure
```text
project/
│
├── backend/                # Server-side environment & API routing
│   ├── app.py              # Main application entry point
│   └── models/             # Regression and statistical calculation scripts
│
├── frontend/               # User interface files
│   ├── index.html          # Main dashboard view
│   ├── css/                # Custom styling stylesheets
│   └── js/                 # Map rendering and API fetch handlers
│
├── data/                   # Geographic and spatial data stores
│   ├── geojson/            # Regional boundary map layers (Mirpur 12, Cities)
│   └── environmental/      # Synthesized CSV coordinate & temperature tables
│
└── documentation/          # System manuals and project presentation mate
