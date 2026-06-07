/**
 * Green Infrastructure Simulation Center
 */

const PRESETS = {
  conservative: { vegetation: 10, trees: 200, roof: 10 },
  moderate: { vegetation: 20, trees: 750, roof: 25 },
  aggressive: { vegetation: 40, trees: 2500, roof: 60 },
};

const CHART_ANIM = { duration: 800, easing: "easeOutQuart" };

let simData = null;
let debounceTimer = null;
const charts = {};

const sliders = {
  vegetation: document.getElementById("slider-vegetation"),
  trees: document.getElementById("slider-trees"),
  roof: document.getElementById("slider-roof"),
};

document.addEventListener("DOMContentLoaded", () => {
  initCharts();
  bindControls();
  runSimulation();
});

function getParams() {
  return {
    region: document.getElementById("sim-region").value,
    vegetationIncrease: Number(sliders.vegetation.value),
    treeCount: Number(sliders.trees.value),
    greenRoofCoverage: Number(sliders.roof.value),
  };
}

function bindControls() {
  Object.entries(sliders).forEach(([key, el]) => {
    el.addEventListener("input", () => {
      updateSliderLabels();
      highlightSlider(key);
      scheduleSimulation();
    });
  });

  document.getElementById("sim-region").addEventListener("change", runSimulation);

  document.getElementById("sim-reset").addEventListener("click", () => {
    applyPreset("moderate");
    document.querySelectorAll(".sim-preset").forEach((b) => {
      b.classList.toggle("is-active", b.dataset.preset === "moderate");
    });
    runSimulation();
  });

  document.querySelectorAll(".sim-preset").forEach((btn) => {
    btn.addEventListener("click", () => {
      applyPreset(btn.dataset.preset);
      document.querySelectorAll(".sim-preset").forEach((b) => b.classList.remove("is-active"));
      btn.classList.add("is-active");
      runSimulation();
    });
  });

  document.querySelector('.sim-preset[data-preset="moderate"]')?.classList.add("is-active");
  updateSliderLabels();
}

function applyPreset(name) {
  const p = PRESETS[name];
  if (!p) return;
  sliders.vegetation.value = p.vegetation;
  sliders.trees.value = p.trees;
  sliders.roof.value = p.roof;
  updateSliderLabels();
}

function updateSliderLabels() {
  document.getElementById("val-vegetation").textContent = `${sliders.vegetation.value}%`;
  document.getElementById("val-trees").textContent = Number(sliders.trees.value).toLocaleString();
  document.getElementById("val-roof").textContent = `${sliders.roof.value}%`;
}

function highlightSlider(key) {
  document.querySelectorAll(".sim-slider-block").forEach((b) => b.classList.remove("is-active"));
  const map = { vegetation: 0, trees: 1, roof: 2 };
  document.querySelectorAll(".sim-slider-block")[map[key]]?.classList.add("is-active");
}

function scheduleSimulation() {
  document.getElementById("sim-status").textContent = "Updating…";
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(runSimulation, 280);
}

function setLoading(on) {
  document.body.classList.toggle("simulation-loading", on);
}

async function runSimulation() {
  const params = getParams();
  setLoading(true);

  try {
    const res = await fetch("/api/simulate-green-infrastructure", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    if (!res.ok) throw new Error("Simulation failed");
    simData = await res.json();
    updateUI(simData);
    document.getElementById("sim-status").textContent = "Live";
  } catch (err) {
    console.error(err);
    document.getElementById("sim-status").textContent = "Error";
  } finally {
    setLoading(false);
  }
}

function updateUI(data) {
  const { before, after, impact, interventionBreakdown, regressionMetrics, formula, locationCount } = data;

  document.getElementById("sim-formula").textContent = formula || "Temperature = α − (β × NDVI)";

  document.getElementById("impact-temp").textContent = `−${impact.temperatureReduction}°C`;
  document.getElementById("impact-temp-delta").textContent =
    `${before.temperature}°C → ${after.temperature}°C`;
  document.getElementById("impact-score").textContent = `+${impact.climateScoreImprovement}`;
  document.getElementById("impact-score-delta").textContent =
    `${before.climateScore} → ${after.climateScore} (${after.climateCategory})`;
  document.getElementById("impact-ndvi").textContent = `+${impact.ndviGain}`;
  document.getElementById("impact-ndvi-delta").textContent =
    `${before.ndvi} → ${after.ndvi}`;
  document.getElementById("impact-hri").textContent = `−${(impact.heatRiskReduction * 100).toFixed(1)}%`;
  document.getElementById("impact-hri-delta").textContent =
    `${(before.heatRiskIndex * 100).toFixed(1)}% → ${(after.heatRiskIndex * 100).toFixed(1)}%`;

  document.querySelectorAll(".sim-impact-card").forEach((c) => {
    c.classList.remove("is-updated");
    void c.offsetWidth;
    c.classList.add("is-updated");
  });

  document.getElementById("before-temp").textContent = `${before.temperature}°C`;
  document.getElementById("before-ndvi").textContent = before.ndvi;
  document.getElementById("before-score").textContent = `${before.climateScore}/100`;
  document.getElementById("before-category").textContent = before.climateCategory;

  document.getElementById("after-temp").textContent = `${after.temperature}°C`;
  document.getElementById("after-ndvi").textContent = after.ndvi;
  document.getElementById("after-score").textContent = `${after.climateScore}/100`;
  document.getElementById("after-category").textContent = after.climateCategory;

  document.getElementById("ndvi-breakdown").innerHTML = `
    <li><span>Vegetation increase</span><span>+${interventionBreakdown.vegetationNdviBoost}</span></li>
    <li><span>Tree plantation</span><span>+${interventionBreakdown.treeNdviBoost}</span></li>
    <li><span>Green roofs</span><span>+${interventionBreakdown.greenRoofNdviBoost}</span></li>
  `;

  document.getElementById("model-r2").textContent = regressionMetrics?.r2Score ?? "—";
  document.getElementById("model-rmse").textContent = regressionMetrics?.rmse ?? "—";
  document.getElementById("model-points").textContent = locationCount ?? "—";

  document.getElementById("sim-recommendation").innerHTML = buildRecommendation(data);

  updateCompareChart(before, after);
  updateComponentChart(before, after);
  updateSensitivityChart(data);
}

function buildRecommendation(data) {
  const { impact, inputs, after } = data;
  const reduction = impact.temperatureReduction;
  const gain = impact.climateScoreImprovement;

  if (reduction < 0.1 && gain < 1) {
    return "<strong>Minimal impact projected.</strong> Increase vegetation, tree planting, or green roof coverage to achieve meaningful urban cooling.";
  }
  if (reduction >= 1.5) {
    return `<strong>High-impact strategy.</strong> Planting <strong>${inputs.treePlantationCount.toLocaleString()}</strong> trees with <strong>${inputs.greenRoofCoverage}%</strong> green roof coverage and <strong>${inputs.vegetationIncreasePercent}%</strong> vegetation growth could reduce surface temperature by <strong>${reduction}°C</strong>, elevating climate resilience to <strong>${after.climateCategory}</strong> (${after.climateScore}/100).`;
  }
  return `<strong>Moderate cooling projected.</strong> Current intervention yields <strong>${reduction}°C</strong> temperature reduction and <strong>+${gain}</strong> climate score points. Consider increasing tree plantation for greater canopy shading.`;
}

function chartBase() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: CHART_ANIM,
    plugins: {
      legend: {
        labels: { color: "#94a3b8", font: { family: "Instrument Sans", size: 11 } },
      },
      tooltip: {
        backgroundColor: "rgba(18, 28, 48, 0.96)",
        titleFont: { family: "Instrument Sans" },
        bodyFont: { family: "DM Sans" },
        padding: 12,
        cornerRadius: 8,
      },
    },
  };
}

function initCharts() {
  charts.compare = new Chart(document.getElementById("compare-chart"), {
    type: "bar",
    data: { labels: ["Temperature (°C)", "NDVI", "Climate Score", "Heat Risk (%)"], datasets: [] },
    options: {
      ...chartBase(),
      scales: {
        y: { grid: { color: "rgba(255,255,255,0.06)" }, ticks: { color: "#94a3b8" } },
        x: { grid: { display: false }, ticks: { color: "#94a3b8", font: { size: 10 } } },
      },
    },
  });

  charts.component = new Chart(document.getElementById("component-chart"), {
    type: "radar",
    data: { labels: ["NDVI", "Temperature", "Low Risk", "Green Cover"], datasets: [] },
    options: {
      ...chartBase(),
      scales: {
        r: {
          angleLines: { color: "rgba(255,255,255,0.08)" },
          grid: { color: "rgba(255,255,255,0.08)" },
          pointLabels: { color: "#94a3b8", font: { size: 9 } },
          ticks: { display: false },
          suggestedMin: 0,
          suggestedMax: 100,
        },
      },
    },
  });

  charts.sensitivity = new Chart(document.getElementById("sensitivity-chart"), {
    type: "line",
    data: { labels: [], datasets: [] },
    options: {
      ...chartBase(),
      scales: {
        y: {
          title: { display: true, text: "Projected temperature (°C)", color: "#94a3b8" },
          grid: { color: "rgba(255,255,255,0.06)" },
          ticks: { color: "#94a3b8" },
        },
        x: {
          title: { display: true, text: "Vegetation increase (%)", color: "#94a3b8" },
          grid: { display: false },
          ticks: { color: "#94a3b8" },
        },
      },
    },
  });
}

function updateCompareChart(before, after) {
  charts.compare.data.datasets = [
    {
      label: "Baseline",
      data: [
        before.temperature,
        before.ndvi * 100,
        before.climateScore,
        before.heatRiskIndex * 100,
      ],
      backgroundColor: "rgba(249, 115, 22, 0.55)",
      borderColor: "#f97316",
      borderWidth: 2,
      borderRadius: 8,
    },
    {
      label: "Projected",
      data: [
        after.temperature,
        after.ndvi * 100,
        after.climateScore,
        after.heatRiskIndex * 100,
      ],
      backgroundColor: "rgba(34, 197, 94, 0.55)",
      borderColor: "#22c55e",
      borderWidth: 2,
      borderRadius: 8,
    },
  ];
  charts.compare.update("active");
}

function updateComponentChart(before, after) {
  const toRadar = (state) => [
    state.breakdown.ndvi.componentScore,
    state.breakdown.averageTemperature.componentScore,
    state.breakdown.heatRiskIndex.componentScore,
    state.breakdown.greenCoveragePercentage.componentScore,
  ];

  charts.component.data.datasets = [
    {
      label: "Baseline",
      data: toRadar(before),
      borderColor: "#f97316",
      backgroundColor: "rgba(249, 115, 22, 0.2)",
      borderWidth: 2,
      pointRadius: 3,
    },
    {
      label: "Projected",
      data: toRadar(after),
      borderColor: "#22c55e",
      backgroundColor: "rgba(34, 197, 94, 0.2)",
      borderWidth: 2,
      pointRadius: 3,
    },
  ];
  charts.component.update("active");
}

function updateSensitivityChart(data) {
  const { before } = data;
  const alpha = data.coefficients?.alpha ?? 32;
  const beta = data.coefficients?.beta ?? 6.5;

  const steps = [0, 5, 10, 15, 20, 25, 30, 40, 50];
  const currentTrees = data.inputs.treePlantationCount;
  const currentRoof = data.inputs.greenRoofCoverage;
  const treeBoost = Math.min(0.18, currentTrees * 0.00004);
  const roofBoost = Math.min(0.14, currentRoof * 0.0012);

  const projected = steps.map((pct) => {
    const vegBoost = before.ndvi * (pct / 100);
    const ndvi = Math.min(0.8, Math.max(-0.3, before.ndvi + vegBoost + treeBoost + roofBoost));
    return round(alpha - beta * ndvi, 2);
  });

  charts.sensitivity.data.labels = steps.map((s) => `${s}%`);
  charts.sensitivity.data.datasets = [
    {
      label: "Baseline",
      data: steps.map(() => before.temperature),
      borderColor: "#f97316",
      borderDash: [6, 4],
      borderWidth: 2,
      pointRadius: 0,
      fill: false,
    },
    {
      label: "Projected cooling curve",
      data: projected,
      borderColor: "#22c55e",
      backgroundColor: "rgba(34, 197, 94, 0.12)",
      fill: true,
      tension: 0.35,
      pointRadius: 4,
      pointBackgroundColor: steps.map((s) =>
        s === data.inputs.vegetationIncreasePercent ? "#38bdf8" : "#22c55e"
      ),
      pointBorderColor: "#fff",
      pointBorderWidth: 2,
    },
  ];
  charts.sensitivity.update("active");
}

function round(n, d) {
  return Math.round(n * Math.pow(10, d)) / Math.pow(10, d);
}
