/**
 * Advanced Climate Analytics — Interactive reporting dashboard
 */

const CITY_COLORS = {
  dhaka_all: "#ef4444",
  mirpur12: "#f97316",
  sylhet: "#22c55e",
  rajshahi: "#eab308",
  chittagong: "#38bdf8",
};

const RISK_COLORS = {
  "Very Low": "#38bdf8",
  Low: "#22c55e",
  Moderate: "#eab308",
  High: "#f97316",
  Extreme: "#ef4444",
};

const CHART_ANIMATION = {
  duration: 900,
  easing: "easeOutQuart",
};

let analyticsData = null;
let hybridData = null;
let validationData = null;
let selectedCities = new Set(["dhaka_all", "mirpur12", "sylhet", "rajshahi", "chittagong"]);
let activeMetric = "temperature";
let selectedYear = null;

const charts = {};

document.addEventListener("DOMContentLoaded", () => {
  loadAnalytics();
  bindMetricToggles();
});

function setLoading(isLoading) {
  document.body.classList.toggle("analytics-loading", isLoading);
}

async function loadAnalytics() {
  setLoading(true);
  try {
    const [climateRes, hybridRes, validationRes] = await Promise.all([
      fetch("/api/climate-analytics"),
      fetch("/api/hybrid-forecast"),
      fetch("/api/model-validation"),
    ]);
    if (!climateRes.ok) throw new Error("Failed to load climate analytics.");
    analyticsData = await climateRes.json();
    hybridData = hybridRes.ok ? await hybridRes.json() : null;
    validationData = validationRes.ok ? await validationRes.json() : null;

    populateKpis();
    buildCityChips();
    buildYearChips();
    initCharts();
    updateAllCharts();
    renderValidationTable();
    updateHybridChart();
    if (analyticsData.regions?.length) {
      openDrilldown(analyticsData.regions[0]);
    }
    const latestYear = analyticsData.historical?.annual?.slice(-1)[0]?.year;
    if (latestYear) selectYear(latestYear);
  } catch (err) {
    console.error(err);
    alert("Unable to load climate analytics. Ensure the backend is running.");
  } finally {
    setLoading(false);
  }
}

function populateKpis() {
  const { comparison, forecast, regions, generatedAt } = analyticsData;
  document.getElementById("kpi-city-count").textContent = String(regions.length);
  document.getElementById("kpi-hottest").textContent = comparison.hottestCity;
  document.getElementById("kpi-resilient").textContent = comparison.mostResilient;
  document.getElementById("kpi-risk").textContent = comparison.highestRisk;
  const trend = forecast?.annualTrendCPerYear;
  document.getElementById("kpi-trend").textContent = trend != null
    ? `${trend >= 0 ? "+" : ""}${trend}°C/yr`
    : "—";
  if (generatedAt) {
    const d = new Date(generatedAt);
    document.getElementById("report-generated").textContent =
      `Report generated ${d.toLocaleString()}`;
  }
}

function getActiveRegions() {
  return analyticsData.regions.filter((r) => selectedCities.has(r.id));
}

function buildCityChips() {
  const container = document.getElementById("city-chips");
  container.innerHTML = "";
  analyticsData.regions.forEach((region) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `city-chip${selectedCities.has(region.id) ? " is-active" : ""}`;
    btn.textContent = region.shortName;
    btn.dataset.id = region.id;
    btn.style.setProperty("--chip-color", CITY_COLORS[region.id]);
    if (selectedCities.has(region.id)) {
      btn.style.background = CITY_COLORS[region.id];
    }
    btn.addEventListener("click", () => toggleCity(region.id, btn));
    container.appendChild(btn);
  });
}

function toggleCity(id, btn) {
  if (selectedCities.has(id)) {
    if (selectedCities.size <= 1) return;
    selectedCities.delete(id);
    btn.classList.remove("is-active");
    btn.style.background = "";
  } else {
    selectedCities.add(id);
    btn.classList.add("is-active");
    btn.style.background = CITY_COLORS[id];
  }
  updateComparisonChart();
  updateRadarChart();
  updateRiskChart();
}

function buildYearChips() {
  const container = document.getElementById("year-chips");
  const years = [...new Set(analyticsData.historical.annual.map((a) => a.year))].sort();
  container.innerHTML = "";
  years.forEach((year) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "year-chip";
    btn.textContent = String(year);
    btn.dataset.year = year;
    btn.addEventListener("click", () => selectYear(year));
    container.appendChild(btn);
  });
}

function selectYear(year) {
  selectedYear = year;
  document.querySelectorAll(".year-chip").forEach((chip) => {
    chip.classList.toggle("is-active", Number(chip.dataset.year) === year);
  });
  document.getElementById("monthly-subtitle").textContent =
    `Monthly thermal profile for ${year}`;
  updateMonthlyChart();
}

function bindMetricToggles() {
  document.querySelectorAll(".metric-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".metric-toggle").forEach((b) => b.classList.remove("is-active"));
      btn.classList.add("is-active");
      activeMetric = btn.dataset.metric;
      updateComparisonChart();
    });
  });
}

function chartDefaults() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: CHART_ANIMATION,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: {
        labels: {
          color: "#94a3b8",
          font: { family: "Instrument Sans", size: 11 },
          boxWidth: 12,
          padding: 14,
        },
      },
      tooltip: {
        backgroundColor: "rgba(18, 28, 48, 0.96)",
        titleFont: { family: "Instrument Sans", size: 12 },
        bodyFont: { family: "DM Sans", size: 11 },
        padding: 12,
        cornerRadius: 8,
      },
    },
  };
}

function initCharts() {
  charts.comparison = new Chart(document.getElementById("city-comparison-chart"), {
    type: "bar",
    data: { labels: [], datasets: [] },
    options: {
      ...chartDefaults(),
      scales: {
        y: {
          grid: { color: "rgba(255,255,255,0.06)" },
          ticks: { color: "#94a3b8", font: { family: "Instrument Sans" } },
        },
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8", font: { family: "Instrument Sans" } },
        },
      },
      onClick: (_, elements) => {
        if (!elements.length) return;
        const idx = elements[0].index;
        const regions = getActiveRegions();
        if (regions[idx]) openDrilldown(regions[idx]);
      },
    },
  });

  charts.radar = new Chart(document.getElementById("city-radar-chart"), {
    type: "radar",
    data: { labels: [], datasets: [] },
    options: {
      ...chartDefaults(),
      scales: {
        r: {
          angleLines: { color: "rgba(255,255,255,0.08)" },
          grid: { color: "rgba(255,255,255,0.08)" },
          pointLabels: { color: "#94a3b8", font: { size: 10 } },
          ticks: { display: false },
          suggestedMin: 0,
          suggestedMax: 100,
        },
      },
    },
  });

  charts.historical = new Chart(document.getElementById("historical-trend-chart"), {
    type: "line",
    data: { labels: [], datasets: [] },
    options: {
      ...chartDefaults(),
      scales: {
        y: {
          position: "left",
          title: { display: true, text: "Mean temp (°C)", color: "#94a3b8" },
          grid: { color: "rgba(255,255,255,0.06)" },
          ticks: { color: "#94a3b8" },
        },
        y1: {
          position: "right",
          title: { display: true, text: "Heatwave days", color: "#94a3b8" },
          grid: { display: false },
          ticks: { color: "#f97316" },
        },
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8" },
        },
      },
      onClick: (_, elements) => {
        if (!elements.length) return;
        const year = analyticsData.historical.annual[elements[0].index]?.year;
        if (year) selectYear(year);
      },
    },
  });

  charts.monthly = new Chart(document.getElementById("monthly-drill-chart"), {
    type: "bar",
    data: { labels: [], datasets: [] },
    options: {
      ...chartDefaults(),
      plugins: { ...chartDefaults().plugins, legend: { display: false } },
      scales: {
        y: {
          grid: { color: "rgba(255,255,255,0.06)" },
          ticks: { color: "#94a3b8" },
        },
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8", maxRotation: 45 },
        },
      },
    },
  });

  charts.risk = new Chart(document.getElementById("risk-distribution-chart"), {
    type: "bar",
    data: { labels: [], datasets: [] },
    options: {
      ...chartDefaults(),
      scales: {
        x: { stacked: true, grid: { display: false }, ticks: { color: "#94a3b8" } },
        y: { stacked: true, grid: { color: "rgba(255,255,255,0.06)" }, ticks: { color: "#94a3b8" } },
      },
      onClick: (_, elements) => {
        if (!elements.length) return;
        const region = getActiveRegions()[elements[0].index];
        if (region) openDrilldown(region);
      },
    },
  });

  charts.surface = new Chart(document.getElementById("drilldown-surface-chart"), {
    type: "bar",
    data: { labels: [], datasets: [] },
    options: {
      indexAxis: "y",
      ...chartDefaults(),
      plugins: { ...chartDefaults().plugins, legend: { display: false } },
      scales: {
        x: {
          grid: { color: "rgba(255,255,255,0.06)" },
          ticks: { color: "#94a3b8" },
        },
        y: {
          grid: { display: false },
          ticks: { color: "#94a3b8", font: { size: 10 } },
        },
      },
    },
  });

  charts.hybrid = new Chart(document.getElementById("hybrid-forecast-chart"), {
    type: "line",
    data: { labels: [], datasets: [] },
    options: {
      ...chartDefaults(),
      scales: {
        y: {
          title: { display: true, text: "Heat index (°C)", color: "#94a3b8" },
          grid: { color: "rgba(255,255,255,0.06)" },
          ticks: { color: "#94a3b8" },
        },
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8" },
        },
      },
    },
  });
}

function metricValue(region, metric) {
  switch (metric) {
    case "temperature": return region.avgTemp;
    case "ndvi": return region.avgNdvi;
    case "hri": return (region.avgHri ?? 0) * 100;
    case "resilience": return region.climateScore;
    default: return 0;
  }
}

function metricLabel(metric) {
  const map = {
    temperature: "Avg temperature (°C)",
    ndvi: "Average NDVI",
    hri: "Heat Risk Index (%)",
    resilience: "Climate resilience (0–100)",
  };
  return map[metric] || metric;
}

function updateComparisonChart() {
  const regions = getActiveRegions();
  charts.comparison.data.labels = regions.map((r) => r.shortName);
  charts.comparison.data.datasets = [
    {
      label: metricLabel(activeMetric),
      data: regions.map((r) => metricValue(r, activeMetric)),
      backgroundColor: regions.map((r) => `${CITY_COLORS[r.id]}99`),
      borderColor: regions.map((r) => CITY_COLORS[r.id]),
      borderWidth: 2,
      borderRadius: 8,
      borderSkipped: false,
    },
  ];
  charts.comparison.update("active");
}

function updateRadarChart() {
  const regions = getActiveRegions();
  const labels = ["Temperature", "NDVI", "Low Heat Risk", "Resilience", "Green Cover"];
  const maxTemp = Math.max(...analyticsData.regions.map((r) => r.avgTemp));

  charts.radar.data.labels = labels;
  charts.radar.data.datasets = regions.map((r) => ({
    label: r.shortName,
    data: [
      100 - (r.avgTemp / maxTemp) * 100,
      (r.avgNdvi ?? 0) * 100,
      100 - (r.avgHri ?? 0) * 100,
      r.climateScore,
      r.greenCoverage ?? 50,
    ],
    borderColor: CITY_COLORS[r.id],
    backgroundColor: `${CITY_COLORS[r.id]}33`,
    borderWidth: 2,
    pointRadius: 3,
    pointHoverRadius: 5,
  }));
  charts.radar.update("active");
}

function updateHistoricalChart() {
  const annual = analyticsData.historical?.annual || [];
  charts.historical.data.labels = annual.map((a) => String(a.year));
  charts.historical.data.datasets = [
    {
      label: "Annual mean temp (°C)",
      data: annual.map((a) => a.meanTemp),
      borderColor: "#38bdf8",
      backgroundColor: "rgba(56, 189, 248, 0.15)",
      fill: true,
      tension: 0.35,
      pointRadius: 5,
      pointHoverRadius: 7,
      yAxisID: "y",
    },
    {
      label: "Heatwave days (>35°C)",
      data: annual.map((a) => a.heatwaveDays),
      borderColor: "#f97316",
      backgroundColor: "rgba(249, 115, 22, 0.2)",
      type: "bar",
      yAxisID: "y1",
      borderRadius: 4,
    },
  ];
  charts.historical.update("active");
}

function updateMonthlyChart() {
  if (!selectedYear) return;
  const monthly = (analyticsData.historical?.monthly || []).filter((m) => m.year === selectedYear);
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  charts.monthly.data.labels = monthly.map((m) => monthNames[m.month - 1]);
  charts.monthly.data.datasets = [
    {
      label: `Mean temp ${selectedYear}`,
      data: monthly.map((m) => m.meanTemp),
      backgroundColor: monthly.map((m) =>
        m.maxTemp >= 35 ? "rgba(239, 68, 68, 0.7)" : "rgba(56, 189, 248, 0.55)"
      ),
      borderColor: monthly.map((m) => (m.maxTemp >= 35 ? "#ef4444" : "#38bdf8")),
      borderWidth: 1.5,
      borderRadius: 6,
    },
  ];
  charts.monthly.update("active");
}

function updateRiskChart() {
  const regions = getActiveRegions();
  const levels = ["Very Low", "Low", "Moderate", "High", "Extreme"];
  charts.risk.data.labels = regions.map((r) => r.shortName);
  charts.risk.data.datasets = levels.map((level) => ({
    label: level,
    data: regions.map((r) => r.riskDistribution[level] || 0),
    backgroundColor: RISK_COLORS[level],
    borderRadius: 4,
  }));
  charts.risk.update("active");
}

function openDrilldown(region) {
  document.getElementById("drilldown-empty").hidden = true;
  const content = document.getElementById("drilldown-content");
  content.hidden = false;

  const color = CITY_COLORS[region.id];

  document.getElementById("drilldown-hero").innerHTML = `
    <h3>${region.name}</h3>
    <p style="color:var(--text-muted);font-size:0.75rem;margin-top:4px;">
      ${region.locationCount} monitoring points · R² ${region.r2Score ?? "—"}
    </p>
    <span class="drilldown-hero__badge" style="color:${color};background:${color}22;border-color:${color}55">
      ${region.climateCategory} · ${region.climateScore}/100
    </span>
  `;

  document.getElementById("drilldown-metrics").innerHTML = `
    <div class="drilldown-metric">
      <span class="drilldown-metric__label">Temperature</span>
      <span class="drilldown-metric__value">${region.avgTemp}°C</span>
    </div>
    <div class="drilldown-metric">
      <span class="drilldown-metric__label">NDVI</span>
      <span class="drilldown-metric__value">${region.avgNdvi}</span>
    </div>
    <div class="drilldown-metric">
      <span class="drilldown-metric__label">Heat Risk</span>
      <span class="drilldown-metric__value">${((region.avgHri ?? 0) * 100).toFixed(1)}%</span>
    </div>
    <div class="drilldown-metric">
      <span class="drilldown-metric__label">High risk areas</span>
      <span class="drilldown-metric__value">${region.highRiskCount}</span>
    </div>
    <div class="drilldown-metric">
      <span class="drilldown-metric__label">Green coverage</span>
      <span class="drilldown-metric__value">${region.greenCoverage}%</span>
    </div>
    <div class="drilldown-metric">
      <span class="drilldown-metric__label">Active alerts</span>
      <span class="drilldown-metric__value">${region.alertCount}</span>
    </div>
  `;

  const surfaces = region.surfaceBreakdown || [];
  charts.surface.data.labels = surfaces.map((s) => s.surface);
  charts.surface.data.datasets = [
    {
      data: surfaces.map((s) => s.meanTemp),
      backgroundColor: surfaces.map((s) =>
        s.meanTemp >= 35 ? "#ef4444aa" : s.meanTemp >= 32 ? "#f97316aa" : "#22c55eaa"
      ),
      borderColor: surfaces.map((s) =>
        s.meanTemp >= 35 ? "#ef4444" : s.meanTemp >= 32 ? "#f97316" : "#22c55e"
      ),
      borderWidth: 1.5,
      borderRadius: 4,
    },
  ];
  charts.surface.update("active");

  const list = document.getElementById("drilldown-hotspots");
  list.innerHTML = (region.hotspots || [])
    .map(
      (h) => `
      <li>
        <span>${h.name}</span>
        <span class="drilldown-hotspots__temp">${h.temperature}°C</span>
      </li>`
    )
    .join("");

  loadDrilldownForecast(region.id);
}

async function loadDrilldownForecast(regionId) {
  const grid = document.getElementById("drilldown-forecast-grid");
  if (!grid) return;
  grid.innerHTML = "<span>Loading forecast…</span>";

  try {
    const res = await fetch(`/api/predict-temperature?region=${regionId}`);
    if (!res.ok) throw new Error("Forecast unavailable");
    const data = await res.json();
    grid.innerHTML = `
      <div class="drilldown-forecast__item"><span>Current</span><strong>${data.currentTemperature}°C</strong></div>
      <div class="drilldown-forecast__item"><span>+1 yr</span><strong>${data.predicted1Year}°C</strong></div>
      <div class="drilldown-forecast__item"><span>+3 yr</span><strong>${data.predicted3Years}°C</strong></div>
      <div class="drilldown-forecast__item"><span>+5 yr</span><strong>${data.predicted5Years}°C</strong></div>
    `;
  } catch {
    grid.innerHTML = "<span>Forecast unavailable for this region.</span>";
  }
}

function renderValidationTable() {
  const tbody = document.getElementById("validation-table-body");
  if (!tbody || !validationData?.regions?.length) {
    if (tbody) tbody.innerHTML = "<tr><td colspan='6'>Validation metrics unavailable.</td></tr>";
    return;
  }

  tbody.innerHTML = validationData.regions
    .map(
      (row) => `
    <tr>
      <td>${row.name}</td>
      <td><span class="validation-tag validation-tag--${row.dataClass || "unknown"}">${row.dataClassLabel || "—"}</span></td>
      <td>${row.linearRegression?.r2 ?? "—"}</td>
      <td>${row.linearRegression?.rmse ?? "—"}</td>
      <td>${row.decisionTree?.r2_score ?? "—"}</td>
      <td>${row.randomForest?.r2_score ?? "—"}</td>
    </tr>`
    )
    .join("");
}

function updateHybridChart() {
  if (!charts.hybrid || !hybridData) return;

  const observed = hybridData.observedSeries || [];
  const projected = hybridData.projectionSeries || [];
  const years = [
    ...new Set([
      ...observed.map((row) => row.Year),
      ...projected.map((row) => row.Year),
    ]),
  ].sort((a, b) => a - b);

  const observedMap = Object.fromEntries(observed.map((row) => [row.Year, row.Heat_Index]));
  const projectedMap = Object.fromEntries(projected.map((row) => [row.Year, row.Heat_Index]));

  charts.hybrid.data.labels = years.map(String);
  charts.hybrid.data.datasets = [
    {
      label: "Observed baseline",
      data: years.map((year) => observedMap[year] ?? null),
      borderColor: "#38bdf8",
      backgroundColor: "rgba(56, 189, 248, 0.12)",
      fill: false,
      tension: 0.3,
      spanGaps: false,
    },
    {
      label: hybridData.bestHybridModel || "Hybrid projection",
      data: years.map((year) => projectedMap[year] ?? null),
      borderColor: "#f97316",
      backgroundColor: "rgba(249, 115, 22, 0.15)",
      borderDash: [6, 4],
      fill: false,
      tension: 0.3,
      spanGaps: false,
    },
  ];
  charts.hybrid.update("active");

  const subtitle = document.getElementById("hybrid-subtitle");
  if (subtitle) {
    const r2 = validationData?.summary?.bestHybridR2;
    subtitle.textContent = r2 != null
      ? `${hybridData.bestHybridModel} · best hybrid R² ${r2}`
      : `${hybridData.bestHybridModel} · 2027–2030 heat-index projection`;
  }
}

function updateAllCharts() {
  updateComparisonChart();
  updateRadarChart();
  updateHistoricalChart();
  updateRiskChart();
}
