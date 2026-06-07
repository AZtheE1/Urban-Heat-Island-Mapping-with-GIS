/**
 * Environmental Command Center — Dashboard Controller
 * -------------------------------------------------------------
 * COLLABORATION BOUNDARIES:
 * - Pair A (GIS): Update `renderMapData()` with actual satellite rasters/geojson.
 * - Pair B (Backend/Analytics): Update `fetchHeatData()` or create extra analytic triggers.
 * - Pair C (Frontend/UI): Style layers, update transitions, enhance Chart.js configs.
 * - Pair D (PMs/Writers): Verify coordinate fields, synthesize mock files, trace stats.
 */

let mapEngine;
let comparisonChart;

const HEAT_COLORS = {
  extreme: "#ef4444",
  high: "#f97316",
  moderate: "#eab308",
  vegetation: "#22c55e",
  cool: "#38bdf8",
};

const HRI_LEVELS = {
  extreme: { min: 0.8, label: "Extreme", color: HEAT_COLORS.extreme },
  high: { min: 0.6, label: "High", color: HEAT_COLORS.high },
  moderate: { min: 0.4, label: "Moderate", color: HEAT_COLORS.moderate },
  low: { min: 0.2, label: "Low", color: HEAT_COLORS.vegetation },
  veryLow: { min: 0, label: "Very Low", color: HEAT_COLORS.cool },
};

const RESILIENCE_COLORS = {
  Critical: HEAT_COLORS.extreme,
  Poor: HEAT_COLORS.high,
  Moderate: HEAT_COLORS.moderate,
  Good: HEAT_COLORS.vegetation,
  Excellent: HEAT_COLORS.cool,
};

const ALERT_COLORS = {
  Extreme: HEAT_COLORS.extreme,
  Severe: HEAT_COLORS.high,
  Warning: HEAT_COLORS.moderate,
  Normal: HEAT_COLORS.vegetation,
};

document.addEventListener("DOMContentLoaded", () => {
  initMap();
  initChart();
  loadRegionData("mirpur12");

  document.getElementById("regionSelect").addEventListener("change", (e) => {
    loadRegionData(e.target.value);
  });

  document.addEventListener("fullscreenchange", () => {
    setTimeout(() => mapEngine?.invalidateSize(), 200);
  });

  window.addEventListener("resize", () => {
    mapEngine?.invalidateSize();
  });
});

function setLoadingState(isLoading) {
  document.body.classList.toggle("is-loading", isLoading);
  const mapWrapper = document.getElementById("map-wrapper");
  if (mapWrapper) {
    mapWrapper.classList.toggle("is-loading-map", isLoading);
  }
}

function showTableSkeleton() {
  const tbody = document.getElementById("table-body");
  tbody.innerHTML = "";
  for (let i = 0; i < 4; i++) {
    const row = document.createElement("tr");
    row.className = "skeleton-row skeleton-live";
    row.innerHTML = `
      <td><div class="skeleton skeleton-cell"></div></td>
      <td><div class="skeleton skeleton-cell"></div></td>
      <td><div class="skeleton skeleton-cell"></div></td>
      <td><div class="skeleton skeleton-cell"></div></td>
    `;
    tbody.appendChild(row);
  }
}

function animateKpiCards() {
  document.querySelectorAll(".command-kpi-card").forEach((card) => {
    card.classList.remove("kpi-animate");
    void card.offsetWidth;
    card.classList.add("kpi-animate");
  });
}

function updateTimestamp() {
  const el = document.getElementById("last-updated");
  if (!el) return;
  const now = new Date();
  el.textContent = `Updated ${now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}`;
}

function getTemperatureColor(temp) {
  if (temp >= 35) return HEAT_COLORS.extreme;
  if (temp >= 32) return HEAT_COLORS.high;
  if (temp >= 30) return HEAT_COLORS.moderate;
  if (temp < 30) return HEAT_COLORS.vegetation;
  return HEAT_COLORS.cool;
}

function getTemperatureClass(temp) {
  if (temp >= 35) return "temp-extreme";
  if (temp >= 32) return "temp-high";
  if (temp >= 30) return "temp-moderate";
  return "temp-vegetation";
}

function classifyHriLevel(hri) {
  if (hri >= HRI_LEVELS.extreme.min) return HRI_LEVELS.extreme;
  if (hri >= HRI_LEVELS.high.min) return HRI_LEVELS.high;
  if (hri >= HRI_LEVELS.moderate.min) return HRI_LEVELS.moderate;
  if (hri >= HRI_LEVELS.low.min) return HRI_LEVELS.low;
  return HRI_LEVELS.veryLow;
}

function initMap() {
  mapEngine = new MapEngine({
    containerId: "map-container",
    wrapperId: "map-wrapper",
    colors: HEAT_COLORS,
  });
  mapEngine.init();
}

async function loadRegionData(regionId) {
  setLoadingState(true);
  showTableSkeleton();
  animateKpiCards();

  try {
    const [heatRes, climateRes, riskRes, alertsRes, recRes, predictRes, provenanceRes, validationRes] =
      await Promise.all([
      fetch(`/api/heat-data?region=${regionId}`),
      fetch(`/api/climate-score?region=${regionId}`),
      fetch(`/api/heat-risk?region=${regionId}`),
      fetch(`/api/alerts?region=${regionId}`),
      fetch(`/api/recommendations?region=${regionId}`),
      fetch(`/api/predict-temperature?region=${regionId}`),
      fetch(`/api/data-provenance?region=${regionId}`),
      fetch(`/api/model-validation?region=${regionId}`),
    ]);

    if (!heatRes.ok) throw new Error("Heat data API retrieval failure.");

    const data = await heatRes.json();
    const climate = climateRes.ok ? await climateRes.json() : null;
    const risk = riskRes.ok ? await riskRes.json() : null;
    const alerts = alertsRes.ok ? await alertsRes.json() : null;
    const recommendations = recRes.ok ? await recRes.json() : null;
    const prediction = predictRes.ok ? await predictRes.json() : null;
    const provenance = provenanceRes.ok ? await provenanceRes.json() : null;
    const validation = validationRes.ok ? await validationRes.json() : null;

    document.getElementById("region-name-display").innerText = data.name;
    document.getElementById("region-desc-display").innerText = data.description;
    updateProvenanceBadge(provenance);

    const coords = REGION_PRESETS[regionId];
    if (mapEngine) {
      mapEngine.setData({
        records: data.records,
        risk,
        climate,
        recommendations,
        alerts,
        coords,
      });
      mapEngine.flyToRegion(coords);
    }

    updateCommandKpis(data.analytics, climate, risk, alerts);
    updateStatsCards(data.analytics);
    updateRegressionPanel(data.analytics, validation);
    updateForecastPanel(prediction);
    updateProvenancePanel(provenance);
    renderGroundTable(data.records);
    updateChartData(data.records);
    updateTimestamp();

    setTimeout(() => mapEngine?.invalidateSize(), 400);
  } catch (error) {
    console.error("Dashboard error:", error);
    showNotification(
      "Connection failure. Check if backend app.py is running on port 5000.",
      "error"
    );
  } finally {
    setLoadingState(false);
  }
}

function updateCommandKpis(analytics, climate, risk, alerts) {
  const avgTemp = analytics.avg_temp;
  const avgTempEl = document.getElementById("cmd-stat-avg-temp");
  avgTempEl.innerText = `${avgTemp}°C`;
  avgTempEl.className = `command-kpi-value value-live ${getTemperatureClass(avgTemp)}`;

  const legacyTemp = document.getElementById("stat-avg-temp");
  if (legacyTemp) legacyTemp.innerText = `${avgTemp}°C`;

  if (climate?.summary) {
    const ndvi = climate.summary.avgNdvi;
    const ndviEl = document.getElementById("cmd-stat-avg-ndvi");
    ndviEl.innerText = roundTo(ndvi, 3);
    ndviEl.style.color = ndvi >= 0.4 ? HEAT_COLORS.vegetation : ndvi >= 0.2 ? HEAT_COLORS.moderate : HEAT_COLORS.high;

    const hri = climate.summary.avgHeatRiskIndex;
    const hriLevel = classifyHriLevel(hri);
    const hriEl = document.getElementById("cmd-stat-hri");
    hriEl.innerText = roundTo(hri * 100, 1) + "%";
    hriEl.style.color = hriLevel.color;
    document.getElementById("cmd-stat-hri-level").innerText = `${hriLevel.label} composite risk`;

    const score = climate.climateResilienceScore;
    const scoreEl = document.getElementById("cmd-stat-climate-score");
    scoreEl.innerText = `${Math.round(score)}/100`;
    scoreEl.style.color = RESILIENCE_COLORS[climate.category] || HEAT_COLORS.cool;
    document.getElementById("cmd-stat-climate-category").innerText = climate.category;
  } else {
    document.getElementById("cmd-stat-avg-ndvi").innerText = "--";
    document.getElementById("cmd-stat-hri").innerText = "--";
    document.getElementById("cmd-stat-climate-score").innerText = "--";
  }

  if (risk?.records) {
    const highRiskCount = risk.records.filter(
      (r) => r.riskLevel === "High" || r.riskLevel === "Extreme"
    ).length;
    const riskEl = document.getElementById("cmd-stat-high-risk");
    riskEl.innerText = String(highRiskCount);
    riskEl.style.color = highRiskCount > 0 ? HEAT_COLORS.extreme : HEAT_COLORS.vegetation;
  } else {
    document.getElementById("cmd-stat-high-risk").innerText = "--";
  }

  if (alerts) {
    const count = alerts.activeAlertCount ?? 0;
    const alertEl = document.getElementById("cmd-stat-alerts");
    alertEl.innerText = String(count);
    const level = alerts.highestLevel || "Normal";
    alertEl.style.color = ALERT_COLORS[level] || HEAT_COLORS.vegetation;
    const levelEl = document.getElementById("cmd-stat-alert-level");
    levelEl.innerText = count > 0 ? `Highest: ${level}` : "No active heatwave alerts";
    levelEl.style.color = ALERT_COLORS[level] || "inherit";
  } else {
    document.getElementById("cmd-stat-alerts").innerText = "--";
  }
}

function updateStatsCards(analytics) {
  document.getElementById("stat-r2").innerText = analytics.r2_score;
  document.getElementById("stat-hotspot").innerText = `${analytics.peak_hotspot.temp}°C`;
  document.getElementById("stat-hotspot-loc").innerText = analytics.peak_hotspot.name;

  let level = "Safe";
  let color = HEAT_COLORS.vegetation;
  if (analytics.avg_temp > 35) {
    level = "Extreme Danger";
    color = HEAT_COLORS.extreme;
  } else if (analytics.avg_temp > 33) {
    level = "High Hazard";
    color = HEAT_COLORS.high;
  } else if (analytics.avg_temp > 30) {
    level = "Moderate Alert";
    color = HEAT_COLORS.moderate;
  }

  const riskBadge = document.getElementById("stat-risk-badge");
  riskBadge.innerText = level;
  riskBadge.style.color = color;
}

function updateRegressionPanel(analytics, validation) {
  document.getElementById("formula-display").innerHTML =
    `Predicted Temp = ${analytics.alpha_intercept} - (${analytics.beta_slope} &times; NDVI)`;
  document.getElementById("stat-rmse").innerText = analytics.rmse;
  document.getElementById("stat-mae").innerText = analytics.mae;

  const regional = validation?.regions?.[0];
  const dtR2 = regional?.decisionTree?.r2_score ?? analytics.decision_tree?.r2_score;
  const rfR2 = regional?.randomForest?.r2_score ?? analytics.random_forest?.r2_score;
  document.getElementById("stat-dt-r2").innerText = dtR2 != null ? dtR2 : "--";
  document.getElementById("stat-rf-r2").innerText = rfR2 != null ? rfR2 : "--";
}

function updateForecastPanel(prediction) {
  if (!prediction) {
    document.getElementById("forecast-current").innerText = "--°C";
    document.getElementById("forecast-1y").innerText = "--°C";
    document.getElementById("forecast-3y").innerText = "--°C";
    document.getElementById("forecast-5y").innerText = "--°C";
    document.getElementById("forecast-meta").innerText = "Forecast unavailable for this region.";
    return;
  }

  document.getElementById("forecast-current").innerText = `${prediction.currentTemperature}°C`;
  document.getElementById("forecast-1y").innerText = `${prediction.predicted1Year ?? "—"}°C`;
  document.getElementById("forecast-3y").innerText = `${prediction.predicted3Years ?? "—"}°C`;
  document.getElementById("forecast-5y").innerText = `${prediction.predicted5Years ?? "—"}°C`;

  const evalMetrics = prediction.evaluation;
  document.getElementById("forecast-meta").innerText =
    `${prediction.model} · base ${prediction.baseYear} · R² ${evalMetrics?.r2 ?? "—"} · ${prediction.dataSource}`;
}

function updateProvenancePanel(provenance) {
  const region = provenance?.regions?.[0];
  if (!region) {
    document.getElementById("provenance-class").innerText = "Data source unavailable";
    document.getElementById("provenance-source").innerText = "";
    document.getElementById("provenance-fusion").innerText = "";
    return;
  }

  document.getElementById("provenance-class").innerText = region.dataClassLabel;
  document.getElementById("provenance-class").className =
    `provenance-card__class provenance-card__class--${region.dataClass}`;
  document.getElementById("provenance-source").innerText =
    `${region.surveyType} · ${region.pointCount} points · ${region.source}`;
  document.getElementById("provenance-fusion").innerText = region.satelliteIntegration;
}

function updateProvenanceBadge(provenance) {
  const badge = document.getElementById("region-data-badge");
  if (!badge) return;
  const region = provenance?.regions?.[0];
  if (!region) {
    badge.textContent = "GIS layer overlays enabled";
    return;
  }
  badge.textContent = region.dataClassLabel;
  badge.className = `collab-badge ${region.dataClass === "ground_truth" ? "collab-c" : "collab-b"}`;
}

function renderGroundTable(records) {
  const tbody = document.getElementById("table-body");
  tbody.innerHTML = "";

  const sorted = [...records].sort((a, b) => b.Temperature - a.Temperature).slice(0, 7);

  sorted.forEach((point) => {
    const row = document.createElement("tr");
    const tempClass = getTemperatureClass(point.Temperature);
    const displayName = point.LocationName.replace("Mirpur 12 ", "");
    row.innerHTML = `
      <td>${displayName}</td>
      <td class="${tempClass}" style="font-weight:700;">${point.Temperature}°C</td>
      <td>${point.NDVI}</td>
      <td><span class="collab-badge collab-c">${point.SurfaceType}</span></td>
    `;
    tbody.appendChild(row);
  });
}

function initChart() {
  const ctx = document.getElementById("analytics-chart").getContext("2d");

  comparisonChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Concrete", "Asphalt", "Bare Soil", "Vegetation"],
      datasets: [
        {
          label: "Mean temperature (°C) per surface",
          data: [36.5, 34.0, 32.5, 29.5],
          backgroundColor: [
            "rgba(239, 68, 68, 0.55)",
            "rgba(249, 115, 22, 0.55)",
            "rgba(234, 179, 8, 0.55)",
            "rgba(34, 197, 94, 0.55)",
          ],
          borderColor: [
            HEAT_COLORS.extreme,
            HEAT_COLORS.high,
            HEAT_COLORS.moderate,
            HEAT_COLORS.vegetation,
          ],
          borderWidth: 1.5,
          borderRadius: 8,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 600,
        easing: "easeOutQuart",
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(18, 28, 48, 0.95)",
          titleFont: { family: "Instrument Sans" },
          bodyFont: { family: "DM Sans" },
          padding: 12,
          cornerRadius: 8,
        },
      },
      scales: {
        y: {
          grid: { color: "rgba(255, 255, 255, 0.06)" },
          ticks: {
            color: "#94a3b8",
            font: { family: "Instrument Sans", size: 11 },
          },
          min: 20,
        },
        x: {
          grid: { display: false },
          ticks: {
            color: "#94a3b8",
            font: { family: "Instrument Sans", size: 10 },
          },
        },
      },
    },
  });
}

function updateChartData(records) {
  const surfaces = {
    Concrete: [],
    Asphalt: [],
    "Bare Soil": [],
    Vegetation: [],
    "Water Body": [],
  };

  records.forEach((p) => {
    if (surfaces[p.SurfaceType]) {
      surfaces[p.SurfaceType].push(p.Temperature);
    } else {
      surfaces["Bare Soil"].push(p.Temperature);
    }
  });

  const categories = ["Concrete", "Asphalt", "Bare Soil", "Vegetation"];
  const means = categories.map((cat) => {
    const list = surfaces[cat] || [];
    if (list.length === 0) return 0;
    const sum = list.reduce((a, b) => a + b, 0);
    return roundTo(sum / list.length, 1);
  });

  comparisonChart.data.datasets[0].data = means;
  comparisonChart.update("active");
}

function showNotification(msg, type = "success") {
  const hud = document.getElementById("collab-hud");
  const banner = document.createElement("div");
  banner.className = "toast-notice";
  banner.innerText = msg;
  banner.style.borderLeftColor =
    type === "success" ? HEAT_COLORS.vegetation : HEAT_COLORS.extreme;

  hud.appendChild(banner);
  setTimeout(() => {
    banner.style.opacity = "0";
    banner.style.transform = "translateX(24px)";
    setTimeout(() => banner.remove(), 300);
  }, 4000);
}

function roundTo(num, dec) {
  return Math.round(num * Math.pow(10, dec)) / Math.pow(10, dec);
}
