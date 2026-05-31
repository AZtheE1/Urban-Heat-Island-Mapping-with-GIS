

## **Project 04** 

## **Urban Heat Island Mapping with Remote Sensing and Ground Data** 

For 5 CSE Students – Environmental Science Project 

## **1. Project Overview** 

## **Objective** 

Develop a system to study and visualize the **Urban Heat Island (UHI) effect** by combining: 

- Ground temperature measurements 

- Satellite remote sensing data 

- GIS mapping 

- Data fusion techniques 

- Predictive heat analysis 

pg. 42 

The project aims to: 

- Identify urban heat hotspots 

- Compare temperature differences across urban zones 

- Analyze environmental causes 

- Generate predictive urban heat maps 

## **2. What is Urban Heat Island (UHI)?** 

Urban Heat Island refers to the phenomenon where: 

- Urban areas become hotter than nearby rural areas 

- Concrete, asphalt, buildings, and vehicles absorb heat 

- Lack of vegetation increases temperature 

## **3. Learning Outcomes** 

Students will learn: 

- Environmental temperature monitoring 

- Remote sensing fundamentals 

- Satellite image analysis 

- GIS-based spatial visualization 

- Data fusion techniques 

- Heat map generation 

- Predictive environmental modeling 

- Scientific field survey methods 

## **4. Team Structure (5 Students) Student 1 – Field Data Collection Lead Responsibilities** 

- Temperature measurements 

- Sensor handling 

- GPS coordinate recording 

- Environmental observations 

## **Deliverables** 

- Ground temperature dataset 

- GPS-tagged survey records 

## **Student 2 – Remote Sensing & Satellite Data Lead** 

pg. 43 

## **Responsibilities** 

- Download satellite imagery 

- Preprocess remote sensing data 

- Extract land surface temperature 

## **Deliverables** 

- Satellite datasets 

- Remote sensing analysis report 

## **Student 3 – GIS & Spatial Mapping Lead** 

## **Responsibilities** 

- GIS map creation 

- Spatial interpolation 

- Heat hotspot visualization 

## **Deliverables** 

- GIS heat maps 

- Spatial analysis outputs 

## **Student 4 – Data Fusion & Predictive Modeling Lead Responsibilities** 

- Merge satellite and field data 

- Build prediction models 

- Generate future heat predictions 

## **Deliverables** 

- Data fusion pipeline 

- Predictive heat model 

- Accuracy analysis 

## **Student 5 – Dashboard, Visualization & Documentation Lead Responsibilities** 

- Web/dashboard development 

- Data visualization 

pg. 44 

- Final report and presentation 

## **Deliverables** 

- Interactive dashboard 

- Charts/maps 

- Documentation and PPT 

## **5. Problem Statement** 

Urbanization causes: 

- Increased temperatures 

- Reduced thermal comfort 

- Higher energy consumption 

- Health risks 

This project aims to: 

- Detect urban heat zones 

- Analyze temperature variation 

- Support sustainable urban planning 

## **6. System Architecture** 

```
Ground Sensors + GPS Data
```

```
              ↓
```

```
      Satellite Image Data
```

```
              ↓
         Data Fusion
              ↓
      GIS Heat Mapping
```

```
              ↓
```

```
 Predictive Heat Analysis
              ↓
```

```
 Dashboard/Web Interface
```

## **7. Required Hardware & Software Hardware** 

## **Component** 

Digital thermometer/DHT22 GPS-enabled smartphone 

## **Purpose** 

Temperature measurement Coordinate collection 

pg. 45 

## **Component** 

Power bank Laptop 

## **Purpose** 

## Field operation Data analysis 

## **Software** 

## **Software** 

QGIS/ArcGIS Google Earth Engine Python Jupyter Notebook OpenCV (optional) Flask/Django Leaflet.js 

## **Purpose** 

GIS mapping Satellite analysis Data processing ML & analysis Image processing Backend Interactive maps 

## **8. Project Phases** 

## **PHASE 1 – Literature Survey (Week 1) Students should study: Urban Heat Island Concepts** 

- Causes of UHI 

- Effects of urbanization 

- Heat retention materials 

- Vegetation cooling effects 

## **Remote Sensing Concepts** 

- Satellite imagery 

- Thermal infrared bands 

- Land Surface Temperature (LST) 

- NDVI vegetation index 

## **GIS Concepts** 

- Spatial interpolation 

- Heat maps 

- Raster data 

## **Deliverables** 

- Literature review 

pg. 46 

- Objectives 

- Study area selection 

## **PHASE 2 – Study Area Selection & Planning (Week 2) Students should choose areas such as:** 

## **Area Type** 

Commercial zone Residential area Park/garden Industrial area Water body area 

**Purpose** High heat Medium heat Cooling comparison Heat source Cooling influence 

**Data Collection Planning** Students should define: 

- Number of sampling locations 

- Time intervals 

- Survey timing (morning/noon/evening) 

## **Suggested Timing** 

**Time Reason** Morning Baseline temperature Afternoon Peak heating Evening Heat retention analysis 

## **Deliverables** 

- Sampling plan 

- Survey schedule 

- Location map 

## **PHASE 3 – Ground Temperature Data Collection (Week 2–3) Objective** 

Collect field temperature measurements. **Data Collection Procedure At Each Location Record:** 

**Parameter Example** GPS coordinates Latitude/Longitude Air temperature °C Surface type Concrete/grass/water 

pg. 47 

## **Parameter** 

Vegetation cover Traffic density Time 

## **Example** 

High/medium/low Low/high Timestamp 

## **Measurement Guidelines** 

- Use same sensor throughout 

- Measure at same height 

- Avoid direct body shading 

- Record readings consistently 

## **Sample Data Table** 

## **Location Temp Latitude Longitude Surface Deliverables** 

- Field dataset 

- GPS-tagged measurements 

- Observation sheets 

## **PHASE 4 – Satellite Data Collection & Processing (Week 3–4) Objective** 

Obtain thermal satellite imagery. 

## **Recommended Satellite Sources** 

**Source Purpose** Landsat 8/9 Thermal imagery Sentinel-2 Land cover MODIS Temperature analysis 

## **Recommended Platforms** 

Students can use: 

- Google Earth Engine 

- USGS Earth Explorer 

## **Data to Extract** 

## **Land Surface Temperature (LST)** 

Shows: 

- Surface heat distribution 

pg. 48 

## **NDVI (Vegetation Index)** 

Shows: 

- Green cover density 

## **Example Analysis** 

Compare: 

- Concrete regions vs parks 

- Dense urban vs vegetation areas 

## **Deliverables** 

## ● Processed satellite images 

- LST maps 

- NDVI maps 

## **PHASE 5 – GIS Mapping & Spatial Analysis (Week 4–5)** 

## **Objective** 

Create urban heat maps. 

## **Step 1 – Import Data into GIS** 

Import: 

- GPS field data 

- Satellite raster data 

## **Step 2 – Create Layers** 

Suggested GIS layers: 

- Temperature points 

- Vegetation 

- Roads 

- Buildings 

- Water bodies 

## **Step 3 – Generate Heat Maps** 

Using: 

pg. 49 

- Interpolation methods 

- Kernel density estimation 

## **Step 4 – Spatial Analysis** 

Analyze: 

- Heat hotspots 

- Cool zones 

- Heat correlation with vegetation 

## **Deliverables** 

- GIS heat maps 

- Spatial analysis report 

## **PHASE 6 – Data Fusion & Predictive Modeling (Week 5–6)** 

## **Objective** 

Combine field and satellite data. 

## **Data Fusion Tasks** 

Merge: 

- Ground temperatures 

- Land surface temperatures 

- NDVI values 

- Urban land use 

## **Suggested Features** 

## **Feature** 

Vegetation index Built-up density Surface type Traffic density 

**Use** Cooling effect Heat generation Heat retention Human activity impact 

## **Machine Learning Models** 

## **Model** 

## **Purpose** 

Linear Regression Temperature prediction Random Forest Nonlinear analysis XGBoost Advanced prediction 

## **Prediction Goals** 

Predict: 

pg. 50 

- Future heat hotspots 

- Temperature distribution 

- Heat risk zones 

## **Performance Metrics** 

- RMSE 

- MAE 

- R² score 

## **Deliverables** 

- Prediction model 

- Heat forecasting outputs 

- Accuracy analysis 

## **PHASE 7 – Dashboard/Web Application (Week 6–7)** 

## **Dashboard Features Interactive Heat Map** 

Display: 

- Temperature zones 

- Hotspots 

- Vegetation regions 

## **Statistical Analysis** 

Show: 

- Average temperatures 

- Hottest locations 

- Heat trends 

## **Comparative Graphs** 

Compare: 

- Urban vs green areas 

- Day vs evening temperatures 

## **Suggested Technologies Frontend** 

pg. 51 

- HTML/CSS/JavaScript 

- Bootstrap 

- React (optional) 

## **Backend** 

- Flask 

- Django 

## **Visualization Libraries** 

- Plotly 

- Leaflet.js 

- Chart.js 

## **Deliverables** 

- Functional dashboard 

- GIS map integration 

- Prediction visualization 

## **PHASE 8 – Validation & Final Testing (Week 8) Students should validate:** 

- Sensor readings 

- GIS heat maps 

- Prediction accuracy 

- Satellite data consistency 

## **Validation Methods** 

Compare: 

- Ground temperature vs satellite LST 

- Urban area vs green zone temperature 

## **9. Suggested Dataset Structure** 

```
Project/
│
├── field_data/
```

```
├── gps_coordinates/
```

> `├── satellite_data/` 

pg. 52 

```
├── gis_maps/
├── ml_models/
```

```
├── backend/
```

```
├── frontend/
```

```
├── dashboard/
```

```
├── documentation/
```

```
└── presentation/
```

## **10. Field Work Safety Guidelines** 

Students should: 

- Avoid extreme afternoon exposure 

- Carry water 

- Work in teams 

- Use sun protection 

- Avoid restricted areas 

## **11. Suggested Weekly Timeline Week Activity** 

- 1 Literature survey 

- 2 Planning & field preparation 

- 3 Temperature data collection 

- 4 Satellite data processing 

- 5 GIS heat mapping 

- 6 Predictive modeling 

- 7 Dashboard development 

- 8 Testing & presentation 

## **12. Evaluation Criteria** 

**Criteria Marks** Field survey quality 15 Remote sensing analysis 20 GIS implementation 20 Predictive modeling 20 Dashboard/application 10 Documentation & presentation 15 **13. Advanced Features (Optional)** Students may additionally implement: 

- Real-time IoT temperature monitoring 

- AI-based heat risk alerts 

pg. 53 

- Mobile app for heat reporting 

- Time-series heat animation 

- Climate adaptation recommendations 

- Smart cooling zone recommendations 

## **14. Expected Final Outcome** 

Students should finally demonstrate: 

- Urban heat hotspot identification 

- Integration of satellite and ground data 

- GIS-based thermal visualization 

- Predictive urban heat analysis 

- Environmental planning support system 

## **15. Viva/Interview Questions** 

1. What is Urban Heat Island effect? 

2. Why are cities hotter than rural areas? 

3. What is remote sensing? 

4. Difference between air temperature and land surface temperature? 

5. What is NDVI? 

6. What is GIS interpolation? 

7. How does Random Forest work? 

8. Why combine satellite and field data? 

9. What factors increase urban heat? 

- 10.Explain your complete project workflow. 

Top of Form 


