/**
 * Urban Heat Island Mapping & Predictive Analytics Dashboard
 * -------------------------------------------------------------
 * COLLABORATION BOUNDARIES:
 * - Pair A (GIS): Update `updateMapOverlays()` with actual satellite rasters/geojson.
 * - Pair B (Backend/Analytics): Update `fetchHeatData()` or create extra analytic triggers.
 * - Pair C (Frontend/UI): Style layers, update transitions, enhance Chart.js configs.
 * - Pair D (PMs/Writers): Verify coordinate fields, synthesize mock files, trace stats.
 */

let map;
let groundMarkerGroup;
let thermalOverlayLayer;
let comparisonChart;

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  initMap();
  initChart();
  
  // Default load of Mirpur 12
  loadRegionData("mirpur12");
  
  // Dropdown event listener
  document.getElementById("regionSelect").addEventListener("change", (e) => {
    loadRegionData(e.target.value);
  });
});

// ==========================================
// PAIR C: Leaflet.js Base Map Initialization
// ==========================================
function initMap() {
  // Center initially over Mirpur 12
  map = L.map("map-container").setView([23.8243, 90.3653], 15);
  
  // High-contrast Dark-mode tiles matching the glassmorphic luxury dashboard aesthetic
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
  }).addTo(map);

  // Group to hold coordinates markers
  groundMarkerGroup = L.layerGroup().addTo(map);
}

// ==========================================
// PAIR B & C: Fetch & Dispatch Data from API
// ==========================================
async function loadRegionData(regionId) {
  try {
    const response = await fetch(`/api/heat-data?region=${regionId}`);
    if (!response.ok) throw new Error("API retrieval failure.");
    
    const data = await response.json();
    
    // Update active HUD summary description
    document.getElementById("region-name-display").innerText = data.name;
    document.getElementById("region-desc-display").innerText = data.description;
    
    // Fly Map to the region coordinates
    const coords = REGION_PRESETS[regionId];
    if (coords) {
      map.flyTo(coords.center, coords.zoom, { animate: true, duration: 1.5 });
    }
    
    // Update Stats Card Widgets (Pair D/B)
    updateStatsCards(data.analytics);
    
    // Render the interactive map overlays (Pair A)
    renderMapData(data.records, coords);
    
    // Update the Regression model equations
    updateRegressionPanel(data.analytics);
    
    // Render comparative tables
    renderGroundTable(data.records);
    
    // Update Chart.js visual comparisons (Pair C)
    updateChartData(data.records);
    
  } catch (error) {
    console.error("Dashboard error:", error);
    showNotification("⚠️ Connection failure. Check if backend app.py is running on port 5000.", "error");
  }
}

// ==========================================
// PAIR D: Update HUD Widgets & Metrics Cards
// ==========================================
function updateStatsCards(analytics) {
  document.getElementById("stat-avg-temp").innerText = `${analytics.avg_temp}°C`;
  document.getElementById("stat-r2").innerText = analytics.r2_score;
  document.getElementById("stat-hotspot").innerText = `${analytics.peak_hotspot.temp}°C`;
  document.getElementById("stat-hotspot-loc").innerText = analytics.peak_hotspot.name;
  
  // Health Risk Scale calculation
  let level = "Safe";
  let color = "var(--accent-neon-green)";
  if (analytics.avg_temp > 35) {
    level = "Extreme Danger";
    color = "var(--accent-neon-red)";
  } else if (analytics.avg_temp > 33) {
    level = "High Hazard";
    color = "var(--accent-gold)";
  } else if (analytics.avg_temp > 30) {
    level = "Moderate Alert";
    color = "var(--accent-neon-blue)";
  }
  
  const riskBadge = document.getElementById("stat-risk-badge");
  riskBadge.innerText = level;
  riskBadge.style.color = color;
}

// ==========================================
// PAIR A & C: Map Layer Hotspots & Markers
// ==========================================
function renderMapData(records, coords) {
  // Clear previous layers
  groundMarkerGroup.clearLayers();
  if (thermalOverlayLayer) {
    map.removeLayer(thermalOverlayLayer);
  }
  
  // 1. Add Ground Sensor coordinate points with tooltips (Synthesized Ground Verification)
  records.forEach(point => {
    let color = "var(--accent-neon-red)"; // Hot
    if (point.Temperature < 31) color = "var(--accent-neon-green)"; // Cool
    else if (point.Temperature < 34) color = "var(--accent-neon-blue)"; // Normal
    
    const circle = L.circleMarker([point.Latitude, point.Longitude], {
      radius: 7,
      fillColor: color,
      color: "#ffffff",
      weight: 1,
      opacity: 0.8,
      fillOpacity: 0.6
    });
    
    let imageTag = point.Image ? `<img src="images/${point.Image}" style="width:100%; border-radius:4px; margin-top:4px; margin-bottom:4px;" alt="Location Image" />` : "";
    circle.bindPopup(`
      <div style="color:#0a0f1d; font-family:sans-serif; font-size:11px; width:160px;">
        <b style="font-size:12px;">${point.LocationName}</b><br/>
        ${imageTag}
        <b>🌡️ Temp:</b> ${point.Temperature}°C<br/>
        <b>🌿 NDVI:</b> ${point.NDVI}<br/>
        <b>🏢 Surface:</b> ${point.SurfaceType}<br/>
        <b>🚗 Traffic:</b> ${point.TrafficDensity}
      </div>
    `);
    
    groundMarkerGroup.addLayer(circle);
  });
  
  // 2. Render heat overlay polygon or bounding grids (Pair A - GIS mock overlay representation)
  if (coords && coords.geojson) {
    thermalOverlayLayer = L.geoJSON(coords.geojson, {
      style: function(feature) {
        let opacity = feature.properties.intensity;
        return {
          color: opacity > 0.6 ? "var(--accent-neon-red)" : "var(--accent-neon-green)",
          weight: 1,
          opacity: 0.2,
          fillColor: opacity > 0.6 ? "var(--accent-neon-red)" : "var(--accent-neon-green)",
          fillOpacity: 0.15
        };
      }
    }).addTo(map);
  }
}

// ==========================================
// PAIR B: Live Regression Engine Display
// ==========================================
function updateRegressionPanel(analytics) {
  document.getElementById("formula-display").innerHTML = 
    `Predicted Temp = ${analytics.alpha_intercept} - (${analytics.beta_slope} &times; NDVI)`;
  document.getElementById("stat-rmse").innerText = analytics.rmse;
  document.getElementById("stat-mae").innerText = analytics.mae;
}

// ==========================================
// PAIR D: Render Ground CSV Table View
// ==========================================
function renderGroundTable(records) {
  const tbody = document.getElementById("table-body");
  tbody.innerHTML = "";
  
  // Show top 6 hotspots first
  const sorted = [...records].sort((a,b) => b.Temperature - a.Temperature).slice(0, 7);
  
  sorted.forEach(point => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${point.LocationName.replace("Mirpur 12 ", "")}</td>
      <td style="font-weight:700; color:${point.Temperature > 34 ? 'var(--accent-neon-red)' : 'var(--text-main)'}">${point.Temperature}°C</td>
      <td>${point.NDVI}</td>
      <td><span class="collab-badge collab-c" style="font-size:9px;">${point.SurfaceType}</span></td>
    `;
    tbody.appendChild(row);
  });
}

// ==========================================
// PAIR C: Chart.js Custom Statistical Plot
// ==========================================
function initChart() {
  const ctx = document.getElementById("analytics-chart").getContext("2d");
  
  comparisonChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Concrete Built-up', 'Asphalt Roads', 'Bare Soil', 'Parks / Vegetation'],
      datasets: [{
        label: 'Mean Temperature (°C) per Surface Profile',
        data: [36.5, 34.0, 32.5, 29.5],
        backgroundColor: [
          'rgba(255, 59, 48, 0.45)', // Red
          'rgba(255, 204, 0, 0.45)', // Gold
          'rgba(0, 122, 255, 0.45)', // Blue
          'rgba(52, 199, 89, 0.45)'  // Green
        ],
        borderColor: [
          'var(--accent-neon-red)',
          'var(--accent-gold)',
          'var(--accent-neon-blue)',
          'var(--accent-neon-green)'
        ],
        borderWidth: 1.5,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#8e9bb2', font: { family: 'Outfit' } },
          min: 20
        },
        x: {
          grid: { display: false },
          ticks: { color: '#8e9bb2', font: { family: 'Outfit' } }
        }
      }
    }
  });
}

function updateChartData(records) {
  // Aggregate averages per surface type
  const surfaces = { 'Concrete': [], 'Asphalt': [], 'Bare Soil': [], 'Vegetation': [], 'Water Body': [] };
  
  records.forEach(p => {
    if (surfaces[p.SurfaceType]) {
      surfaces[p.SurfaceType].push(p.Temperature);
    } else {
      surfaces['Bare Soil'].push(p.Temperature); // Fallback
    }
  });
  
  const categories = ['Concrete', 'Asphalt', 'Bare Soil', 'Vegetation'];
  const means = categories.map(cat => {
    const list = surfaces[cat] || [];
    if (list.length === 0) return 0;
    const sum = list.reduce((a,b) => a+b, 0);
    return roundTo(sum / list.length, 1);
  });
  
  comparisonChart.data.datasets[0].data = means;
  comparisonChart.update();
}

function showNotification(msg, type = "success") {
  const hud = document.getElementById("collab-hud");
  const banner = document.createElement("div");
  banner.className = "toast-notice";
  banner.innerText = msg;
  banner.style.borderLeftColor = type === "success" ? "var(--accent-neon-green)" : "var(--accent-neon-red)";
  
  hud.appendChild(banner);
  setTimeout(() => {
    banner.remove();
  }, 4000);
}

function roundTo(num, dec) {
  return Math.round(num * Math.pow(10, dec)) / Math.pow(10, dec);
}
