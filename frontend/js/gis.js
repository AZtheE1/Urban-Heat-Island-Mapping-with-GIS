/**
 * GIS Visualization Center — LST / NDVI / Heat Risk map module
 */

const GIS_LAYERS = ["lst", "ndvi", "heat-risk"];

const CITIES = [
  { id: "mirpur12", label: "Mirpur 12", short: "Mirpur" },
  { id: "dhaka_all", label: "Dhaka", short: "Dhaka" },
  { id: "sylhet", label: "Sylhet", short: "Sylhet" },
  { id: "rajshahi", label: "Rajshahi", short: "Rajshahi" },
  { id: "chittagong", label: "Chittagong", short: "Chittagong" },
];

const LAYER_DESCRIPTIONS = {
  lst: "Land surface temperature markers",
  ndvi: "Normalized Difference Vegetation Index",
  "heat-risk": "Composite heat exposure with gradient overlay",
};

const HEAT_COLORS = {
  extreme: "#ef4444",
  high: "#f97316",
  moderate: "#eab308",
  vegetation: "#22c55e",
  cool: "#38bdf8",
};

let mapEngine;
let currentRegion = "mirpur12";
let uploadedGeoJSON = null;

document.addEventListener("DOMContentLoaded", () => {
  initMap();
  buildCityNav();
  bindGeoJSONControls();
  loadRegion("mirpur12");
});

function initMap() {
  mapEngine = new MapEngine({
    containerId: "map-container",
    wrapperId: "map-wrapper",
    colors: HEAT_COLORS,
    enabledLayers: GIS_LAYERS,
    defaultLayer: "lst",
  });
  mapEngine.init();
}

function buildCityNav() {
  const nav = document.getElementById("gis-city-nav");
  CITIES.forEach((city) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `gis-city-btn${city.id === currentRegion ? " is-active" : ""}`;
    btn.dataset.region = city.id;
    btn.textContent = city.label;
    btn.addEventListener("click", () => {
      if (city.id === currentRegion) return;
      document.querySelectorAll(".gis-city-btn").forEach((b) => {
        b.classList.toggle("is-active", b.dataset.region === city.id);
      });
      loadRegion(city.id);
    });
    nav.appendChild(btn);
  });
}

function bindGeoJSONControls() {
  document.getElementById("geojson-upload").addEventListener("change", handleGeoJSONUpload);
  document.getElementById("geojson-clear").addEventListener("click", clearGeoJSON);
}

async function loadRegion(regionId) {
  currentRegion = regionId;
  setLoading(true);

  try {
    const [heatRes, riskRes, climateRes] = await Promise.all([
      fetch(`/api/heat-data?region=${regionId}`),
      fetch(`/api/heat-risk?region=${regionId}`),
      fetch(`/api/climate-score?region=${regionId}`),
    ]);

    if (!heatRes.ok) throw new Error("Failed to load regional heat data.");

    const heatData = await heatRes.json();
    const risk = riskRes.ok ? await riskRes.json() : null;
    const climate = climateRes.ok ? await climateRes.json() : null;
    const coords = REGION_PRESETS[regionId];

    mapEngine.setData({
      records: heatData.records,
      risk,
      climate,
      coords,
    });

    if (coords) {
      mapEngine.flyToRegion({
        center: coords.center,
        zoom: coords.zoom,
        bounds: coords.bounds,
        geojson: coords.geojson,
      });
    }

    updateSidebar(heatData, coords);
    document.getElementById("gis-updated").textContent =
      `Updated ${new Date().toLocaleTimeString()}`;

    if (uploadedGeoJSON) {
      await analyzeGeoJSON(uploadedGeoJSON);
    } else {
      renderEmptyAnalysis();
    }

    setTimeout(() => mapEngine.invalidateSize(), 400);
  } catch (err) {
    console.error(err);
    document.getElementById("gis-status").textContent = `Error loading ${regionId}: ${err.message}`;
  } finally {
    setLoading(false);
  }
}

function updateSidebar(heatData, coords) {
  const city = CITIES.find((c) => c.id === currentRegion);
  const layer = mapEngine.activeLayer;

  document.getElementById("gis-region-name").textContent = heatData.name || city?.label;
  document.getElementById("gis-point-count").textContent = String(heatData.records?.length || 0);
  document.getElementById("gis-layer-desc").textContent = LAYER_DESCRIPTIONS[layer] || "";
  document.getElementById("gis-status").textContent =
    `${heatData.name} · ${MAP_LAYERS[layer]?.label || layer} layer · ${heatData.records?.length || 0} points`;

  observeLayerChanges();
}

function observeLayerChanges() {
  if (mapEngine._gisLayerObserver) return;

  const panel = document.querySelector(".map-layer-panel__list");
  if (!panel) return;

  panel.addEventListener("click", () => {
    setTimeout(() => {
      const layer = mapEngine.activeLayer;
      document.getElementById("gis-layer-desc").textContent = LAYER_DESCRIPTIONS[layer] || "";
      const name = document.getElementById("gis-region-name").textContent;
      const count = document.getElementById("gis-point-count").textContent;
      document.getElementById("gis-status").textContent =
        `${name} · ${MAP_LAYERS[layer]?.label || layer} layer · ${count} points`;
    }, 400);
  });
  mapEngine._gisLayerObserver = true;
}

async function handleGeoJSONUpload(event) {
  const file = event.target.files?.[0];
  if (!file) return;

  setLoading(true, "Parsing GeoJSON…");

  try {
    const text = await file.text();
    const geojson = JSON.parse(text);
    uploadedGeoJSON = geojson;
    mapEngine.setUserGeoJSON(geojson);
    document.getElementById("geojson-clear").disabled = false;
    await analyzeGeoJSON(geojson);
  } catch (err) {
    console.error(err);
    renderAnalysisError(err.message || "Invalid GeoJSON file.");
  } finally {
    setLoading(false);
    event.target.value = "";
  }
}

async function analyzeGeoJSON(geojson) {
  const panel = document.getElementById("geojson-analysis");
  panel.innerHTML = `<p class="gis-analysis__empty">Analyzing polygon…</p>`;

  try {
    const res = await fetch("/api/analyze-region", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ region: currentRegion, geojson }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Analysis failed");

    renderAnalysisResults(data);
  } catch (err) {
    renderAnalysisError(err.message);
  }
}

function renderAnalysisResults(data) {
  const stats = data.areaStatistics || {};
  const panel = document.getElementById("geojson-analysis");

  if (stats.pointCount === 0) {
    panel.innerHTML = `
      <p class="gis-analysis__warn">${escapeHtml(data.message || "No points inside polygon.")}</p>
      <p class="gis-analysis__meta">Area ≈ ${stats.approximateAreaSqKm ?? "—"} km² · ${stats.polygonCount ?? 0} polygon(s)</p>`;
    return;
  }

  panel.innerHTML = `
    <div class="gis-analysis__stats">
      <div class="gis-analysis__stat">
        <span>Points matched</span>
        <strong>${stats.pointCount} / ${stats.totalRegionalPoints}</strong>
      </div>
      <div class="gis-analysis__stat">
        <span>Coverage</span>
        <strong>${stats.coveragePercentage}%</strong>
      </div>
      <div class="gis-analysis__stat">
        <span>Avg LST</span>
        <strong>${stats.averageTemperature}°C</strong>
      </div>
      <div class="gis-analysis__stat">
        <span>Avg NDVI</span>
        <strong>${stats.averageNdvi}</strong>
      </div>
      <div class="gis-analysis__stat">
        <span>Avg Heat Risk</span>
        <strong>${((stats.averageHeatRiskIndex ?? 0) * 100).toFixed(1)}%</strong>
      </div>
      <div class="gis-analysis__stat">
        <span>Risk level</span>
        <strong>${escapeHtml(stats.heatRiskLevel || "—")}</strong>
      </div>
    </div>
    <p class="gis-analysis__meta">Polygon area ≈ ${stats.approximateAreaSqKm} km²</p>`;
}

function renderAnalysisError(message) {
  document.getElementById("geojson-analysis").innerHTML =
    `<p class="gis-analysis__error">${escapeHtml(message)}</p>`;
}

function renderEmptyAnalysis() {
  document.getElementById("geojson-analysis").innerHTML =
    `<p class="gis-analysis__empty">No polygon loaded. Region preset zones are shown on the map.</p>`;
}

function clearGeoJSON() {
  uploadedGeoJSON = null;
  mapEngine.clearUserGeoJSON();
  document.getElementById("geojson-clear").disabled = true;
  renderEmptyAnalysis();
}

function setLoading(on, msg) {
  document.body.classList.toggle("is-loading", on);
  if (msg) document.getElementById("loader-message").textContent = msg;
}

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

window.addEventListener("resize", () => mapEngine?.invalidateSize());
document.addEventListener("fullscreenchange", () => {
  setTimeout(() => mapEngine?.invalidateSize(), 200);
});
