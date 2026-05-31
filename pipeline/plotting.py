import os
import matplotlib.pyplot as plt
import seaborn as sns

def generate_visualizations(df, meta, graphs_dir, maps_dir):
    """
    Generates Matplotlib comparative scatter plots and an interactive Leaflet.js
    HTML heatmap overlay centered over the selected region.
    """
    region = meta["region"]
    region_name = meta["name"]
    
    # 1. Generate Matplotlib Comparative Plot
    plt.figure(figsize=(8, 5))
    sns.set_theme(style="darkgrid")
    
    # Custom neon aesthetics
    scatter = sns.scatterplot(
        data=df, 
        x="NDVI", 
        y="Temperature", 
        hue="SurfaceType",
        palette={"Concrete": "#e74c3c", "Asphalt": "#f39c12", "Vegetation": "#2ecc71", "Bare Soil": "#9b59b6", "Water Body": "#3498db", "Mixed": "#7f8c8d"},
        s=100,
        alpha=0.8
    )
    
    # Linear trendline
    sns.regplot(
        data=df, 
        x="NDVI", 
        y="Temperature", 
        scatter=False, 
        color="#3498db", 
        line_kws={"linestyle": "--", "linewidth": 2}
    )
    
    plt.title(f"Thermal Disparity: Temperature vs. NDVI ({region_name})", fontsize=12, fontweight="bold")
    plt.xlabel("Normalized Difference Vegetation Index (NDVI)", fontsize=10)
    plt.ylabel("Temperature (°C)", fontsize=10)
    plt.legend(title="Surface Type")
    plt.tight_layout()
    
    graph_filename = f"{region}_concrete_vs_veg_scatter.png"
    graph_path = os.path.join(graphs_dir, graph_filename)
    plt.savefig(graph_path, dpi=150)
    plt.close()
    
    # 2. Generate Interactive Leaflet.js HTML Map
    # We will generate a self-contained premium HTML file using a beautiful template
    lat_center = float(df["Latitude"].mean())
    lng_center = float(df["Longitude"].mean())
    
    # Build JavaScript markers array
    markers_js = ""
    for idx, row in df.iterrows():
        name = row["LocationName"].replace("'", "\\'")
        temp = row["Temperature"]
        surface = row["SurfaceType"]
        ndvi = row["NDVI"]
        lat = row["Latitude"]
        lng = row["Longitude"]
        traffic = row.get("TrafficDensity", "N/A")
        
        # Select color matching the surface profile
        color_map = {
            "Concrete": "#e74c3c",
            "Asphalt": "#f39c12",
            "Vegetation": "#2ecc71",
            "Bare Soil": "#9b59b6",
            "Water Body": "#3498db",
            "Mixed": "#7f8c8d"
        }
        color = color_map.get(surface, "#7f8c8d")
        
        markers_js += f"""
        L.circle([{lat}, {lng}], {{
            color: '{color}',
            fillColor: '{color}',
            fillOpacity: 0.65,
            radius: 80
        }}).addTo(map).bindPopup(`
            <div style="font-family: 'Outfit', sans-serif; min-width: 180px;">
                <h4 style="margin: 0 0 5px 0; color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 3px;">${name}</h4>
                <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                    <tr><td><b>Temperature:</b></td><td style="color: {color};"><b>{temp}°C</b></td></tr>
                    <tr><td><b>Surface Type:</b></td><td>{surface}</td></tr>
                    <tr><td><b>NDVI Index:</b></td><td>{ndvi}</td></tr>
                    <tr><td><b>Traffic Density:</b></td><td>{traffic}</td></tr>
                </table>
            </div>
        `);
        """

    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>UHI GIS Hotspot Overlay - {region_name}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body, html {{ margin: 0; padding: 0; height: 100%; font-family: 'Outfit', sans-serif; background-color: #0f172a; color: #f8fafc; overflow: hidden; }}
        #header {{
            position: absolute; top: 15px; left: 15px; z-index: 1000;
            background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(10px);
            padding: 15px 25px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);
            max-width: 320px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }}
        #header h2 {{ margin: 0 0 5px 0; font-size: 18px; font-weight: 700; color: #38bdf8; }}
        #header p {{ margin: 0; font-size: 12px; color: #94a3b8; line-height: 1.4; }}
        #legend {{
            position: absolute; bottom: 25px; right: 25px; z-index: 1000;
            background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(10px);
            padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 10px 25px rgba(0,0,0,0.5); font-size: 12px;
        }}
        .legend-title {{ font-weight: 600; margin-bottom: 8px; color: #38bdf8; text-transform: uppercase; font-size: 10px; letter-spacing: 1px; }}
        .legend-item {{ display: flex; align-items: center; margin-bottom: 5px; }}
        .legend-color {{ width: 14px; height: 14px; border-radius: 30%; margin-right: 8px; }}
        #map {{ width: 100%; height: 100%; }}
        .leaflet-bar a {{ background-color: rgba(15, 23, 42, 0.9) !important; color: #f8fafc !important; border: 1px solid rgba(255,255,255,0.1) !important; }}
    </style>
</head>
<body>

    <div id="header">
        <h2>🌡️ UHI Overlay: {region_name}</h2>
        <p>{meta["description"]}</p>
    </div>

    <div id="legend">
        <div class="legend-title">Surface Profile & Heat</div>
        <div class="legend-item"><div class="legend-color" style="background: #e74c3c;"></div>Concrete (High Heat)</div>
        <div class="legend-item"><div class="legend-color" style="background: #f39c12;"></div>Asphalt (Medium-High)</div>
        <div class="legend-item"><div class="legend-color" style="background: #9b59b6;"></div>Bare Soil (Medium)</div>
        <div class="legend-item"><div class="legend-color" style="background: #2ecc71;"></div>Vegetation (Cool Zone)</div>
        <div class="legend-item"><div class="legend-color" style="background: #3498db;"></div>Water Body (Cool Sink)</div>
        <div class="legend-item"><div class="legend-color" style="background: #7f8c8d;"></div>Mixed/Other</div>
    </div>

    <div id="map"></div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // Initialize Leaflet Map centered over regional center
        const map = L.map('map', {{
            zoomControl: true,
            maxZoom: 18,
            minZoom: 10
        }}).setView([{lat_center}, {lng_center}], 14);

        // Standard CartoDB Dark Matter tile layer for neon aesthetic
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        }}).addTo(map);

        // Inject computed regional hotspot circle layers
        {markers_js}

    </script>
</body>
</html>
"""
    
    map_filename = f"{region}_heatmap.html"
    map_path = os.path.join(maps_dir, map_filename)
    with open(map_path, "w", encoding="utf-8") as f:
        f.write(html_template)
        
    return graph_path, map_path
