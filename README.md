# 🌡️ Urban Heat Island Mapping & Predictive GIS Dashboard

Welcome to the **Urban Heat Island (UHI) Mapping & Analytics System**. This repository serves as a modular, high-end collaborative boilerplate designed for **Theory Project Group 4 (CSE 3-2)**.

The system is designed around a baseline micro-analysis of **Mirpur 12** and extends macro scaling capabilities across major divisions in Bangladesh: **Entire Dhaka**, **Sylhet**, **Rajshahi**, and **Chittagong**. It correlates high-resolution satellite remote sensing indices (NDVI) with ground-truth verification measurements to identify and predict high-risk thermal hotspot zones.

---

## 👥 Subgroup Collaboration Framework

To ensure seamless integration without merge conflicts, the codebase is split into specific, isolated responsibility spheres:

### 📡 Subgroup A: GIS & Remote Sensing Leads
* **Role:** Handlers of satellite raster data, Land Surface Temperature (LST) extractions, and SVG/GeoJSON border layers.
* **Workspace Boundary:**
  - `data/geojson/`: Drop in your final GeoJSON boundary files or LST grids.
  - Update `placeholders.js` with your refined bounding boxes or shapefiles.

### 🧠 Subgroup B: Backend & Analytics Leads
* **Role:** Keepers of server routing, database queries, and the mathematical prediction engines.
* **Workspace Boundary:**
  - `backend/app.py`: Build endpoints, modify response structures, and handle client requests.
  - `backend/models/analytics.py`: Refine the linear/non-linear prediction scripts ($\text{Predicted Temp} = \alpha - (\beta \times \text{NDVI})$) and accuracy evaluation metrics ($R^2$, RMSE, MAE).

### 🎨 Subgroup C: Frontend & Map UI Leads
* **Role:** UI/UX developers, Leaflet.js rendering, Chart.js integrations, and dynamic responsive dashboard design.
* **Workspace Boundary:**
  - `frontend/index.html`: Dashboard views, statistical cards, and layout elements.
  - `frontend/css/styles.css`: Styling sheets, micro-animations, theme gradients, and typography.
  - `frontend/js/app.js`: Leaflet bindings, dropdown triggers, and API chart re-renderers.

### ✍️ Subgroup D (Our Group): Project Managers & Data Synthesis
* **Role:** Progress controllers, final reports/PPT layout creators, and data synthesis.
* **Workspace Boundary:**
  - `data/environmental/`: Maintain and expand field measurements (such as the 20-coordinate Mirpur 12 ground CSV dataset).
  - Tracking system outputs and writing the technical project manuals.

---

## 📁 Repository Structure

```text
Project/
├── backend/
│   ├── app.py                # Main Flask Server & Routing Hub
│   └── models/
│       └── analytics.py      # Statistical & Predictive Regression Script
├── data/
│   ├── environmental/
│   │   └── mirpur12_ground_data.csv   # Synthesized 20 coordinate ground points (Pair D)
│   └── geojson/
│       └── placeholders.js   # Coordinate offsets & boundaries for mapping layers
├── frontend/
│   ├── index.html            # Core Dashboard UI Layout
│   ├── css/
│   │   └── styles.css        # Luxury Glassmorphic Stylesheet
│   └── js/
│       └── app.js            # Client logic (Leaflet.js & Chart.js connector)
└── README.md                 # Project and collaboration overview
```

---

## 🚀 Quick Launch Instructions

### Prerequisites
Make sure you have **Python 3** and `pip` installed.

### 1. Install Dependencies
Run the following command to install the required lightweight data-science libraries:
```bash
pip install flask pandas numpy scikit-learn
```

### 2. Run the Local Server
From the root project directory, execute:
```bash
python backend/app.py
```

### 3. Open the Dashboard
Open your browser and navigate to:
```text
http://127.0.0.1:5000/
```
The interface will automatically load, default-centered over **Mirpur 12**, showcasing the ground verification coordinates, statistical regression modeling indices, and interactive maps.
