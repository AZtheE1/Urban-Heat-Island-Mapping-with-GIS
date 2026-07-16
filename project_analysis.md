# Project Analysis: Urban Heat Island Mapping & Predictive GIS Analytics System

## ❓ Why We Build This & Purpose
As cities grow, they experience the **Urban Heat Island (UHI) effect**, where urban areas become significantly warmer than their rural surroundings. This phenomenon poses severe health risks and leads to increased energy consumption. 

The purpose of this project is to provide an **Environmental Decision Support System (EDSS)** with actionable, hyper-local intelligence for urban planners and climate researchers. By fusing remote sensing satellite data with ground-truth sensors, the system can:
- Map micro and macro thermal anomalies.
- Predict future temperatures (1, 3, and 5-year forecasts).
- Recommend sustainable urban interventions, such as tree plantations and green roofs, to mitigate heat.

## 🛠️ Main Tech Stack
The architecture relies on a robust Python data pipeline combined with an interactive web dashboard.
- **Data Processing & Analytics:** Python, Pandas, NumPy, Statsmodels
- **Machine Learning:** Scikit-Learn (Linear Regression & Hybrid ML models)
- **Geospatial Mapping:** Folium, Leaflet.js
- **Backend API:** Flask (REST APIs for serving analytics, predictions, and resilience scoring)
- **Frontend Visualization:** HTML5, Custom CSS (Glassmorphism), Chart.js, Plotly

## ⚠️ Issues & Lackings
Based on the current project documentation and structure, there are a few notable gaps:
1. **Live Data Integration:** The system relies on processed datasets/presets rather than real-time satellite imagery APIs (like Google Earth Engine or Copernicus) or live IoT sensor streams.
2. **Advanced GIS Tooling:** The project mentions future integration for shapefile analytics (Geopandas), meaning it might currently lack the ability to process raw spatial boundaries.
3. **Alerting System:** Live alerts for heatwaves are not yet implemented (listed as a future goal using Twilio).
4. **Deployment State:** The project is not fully deployed for public access yet (the live demo URL is just a placeholder).
5. **Performance Bottleneck in API:** The Flask backend (`backend/app.py`) reads static CSV and JSON files from disk (e.g., via `pd.read_csv`) on every single API request (e.g. `/api/heat-data`, `/api/recommendations`). This will severely degrade performance under concurrent load.
6. **Data Type & Calculation Warnings:** The calculations pipeline (`pipeline/calculation.py`) had unhandled scalar casting and float `.round()` method calls on basic types, leading to runtime crashes. (Fixed)
## 💡 Suggestions for the Project
1. **Dockerization:** Containerize the Flask backend and Python pipelines using Docker to ensure consistent environments and easier deployment.
2. **Real-time API Integration:** Integrate open weather and satellite APIs (e.g., NASA Earthdata, Sentinel-2, or Google Earth Engine) for automated, periodic data ingestion.
3. **Authentication & Rate Limiting:** As the API ecosystem expands, implement basic JWT authentication or API keys to prevent abuse of the forecasting and mapping endpoints.
4. **Advanced ML Models:** Transition from basic Scikit-Learn models to Deep Learning approaches (like LSTMs or Spatial-Temporal Graph Neural Networks) for more accurate, time-series-based temperature forecasting.
5. **Implement Server-Side Caching:** Use `functools.lru_cache` or a Redis layer in `backend/app.py` to cache the contents of the generated `.csv` and `.json` datasets. Since these files are only updated periodically by the pipeline, caching them will drastically reduce disk I/O and improve API response times.
6. **Code Profiling & Robust Types:** Ensure consistent `pandas` dataframe column operations instead of iterating or casting manually. Some unnecessary `int()` casts were present in the calculation pipeline.

## 🌍 Is it Deployed?
**No, it is currently not deployed.** 
The README features a "Live Demo" section, but the link provided is a placeholder (`https://your-live-url-here.com`), accompanied by a note to update it with the actual deployment link. The system currently requires manual local setup (installing requirements and running `main.py` & `dashboard/run_dashboard.py`).
