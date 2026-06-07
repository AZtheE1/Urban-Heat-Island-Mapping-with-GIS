/**
 * NDVI–LST Regression Analysis — thesis visualization
 */

let regChart = null;
let regData = null;

const CHART_ANIM = { duration: 800, easing: "easeOutQuart" };

document.addEventListener("DOMContentLoaded", () => {
  initChart();
  document.getElementById("reg-region").addEventListener("change", (e) => {
    loadRegression(e.target.value);
  });
  loadRegression("mirpur12");
});

function setLoading(on) {
  document.body.classList.toggle("is-loading", on);
}

async function loadRegression(regionId) {
  setLoading(true);
  try {
    const res = await fetch(`/api/regression-analysis?region=${regionId}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || "Regression analysis failed");
    }
    regData = await res.json();
    renderAll(regData);
  } catch (err) {
    console.error(err);
    document.getElementById("reg-interpret").innerHTML =
      `<p class="reg-interpret__summary reg-interpret__summary--warn">${escapeHtml(err.message)}</p>`;
  } finally {
    setLoading(false);
  }
}

function renderAll(data) {
  const stats = data.statistics;

  document.getElementById("reg-formula").textContent = data.formulaDisplay;
  document.getElementById("reg-sample-meta").textContent =
    `${data.name} · ${data.sampleCount} observations · ${data.description || ""}`;

  document.getElementById("kpi-alpha").textContent = stats.alphaIntercept;
  document.getElementById("kpi-beta").textContent = stats.betaSlope;
  document.getElementById("kpi-r2").textContent = stats.r2Score;
  document.getElementById("kpi-rmse").textContent = `${stats.rmse}°C`;
  document.getElementById("kpi-corr").textContent = stats.pearsonCorrelation;
  document.getElementById("kpi-corr-label").textContent =
    data.interpretation.correlationStrength + " correlation";

  document.getElementById("reg-chart-subtitle").textContent =
    `NDVI range ${data.ndviRange.min}–${data.ndviRange.max} · LST ${data.lstRange.min}–${data.lstRange.max}°C`;

  renderInterpretation(data.interpretation);
  updateChart(data);
}

function renderInterpretation(interp) {
  const isInverse = interp.pearsonCorrelation < -0.15 && interp.summary.includes("inverse");
  document.getElementById("reg-interpret").innerHTML = `
    <span class="reg-interpret__badge ${isInverse ? "reg-interpret__badge--inverse" : ""}">
      ${escapeHtml(interp.correlationStrength)} correlation (r = ${interp.pearsonCorrelation})
    </span>
    <div class="reg-interpret__summary ${isInverse ? "" : "reg-interpret__summary--warn"}">
      ${escapeHtml(interp.summary)}
    </div>
    <div class="reg-interpret__fit">${escapeHtml(interp.fitQuality)}</div>
    <p><strong>Thesis formula:</strong> ${escapeHtml(interp.thesisFormula)}</p>
  `;
  document.getElementById("reg-methodology").textContent = interp.methodologyNote;
}

function initChart() {
  const ctx = document.getElementById("regression-scatter-chart").getContext("2d");

  regChart = new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Observations",
          data: [],
          backgroundColor: "rgba(56, 189, 248, 0.55)",
          borderColor: "#38bdf8",
          borderWidth: 1.5,
          pointRadius: 7,
          pointHoverRadius: 9,
        },
        {
          label: "Regression line",
          data: [],
          type: "line",
          borderColor: "#a78bfa",
          backgroundColor: "transparent",
          borderWidth: 2.5,
          pointRadius: 0,
          tension: 0,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: CHART_ANIM,
      plugins: {
        legend: {
          labels: {
            color: "#94a3b8",
            font: { family: "Instrument Sans", size: 11 },
          },
        },
        tooltip: {
          backgroundColor: "rgba(18, 28, 48, 0.96)",
          titleFont: { family: "Instrument Sans" },
          bodyFont: { family: "DM Sans", size: 11 },
          callbacks: {
            label(context) {
              if (context.datasetIndex === 0 && regData?.observations?.[context.dataIndex]) {
                const obs = regData.observations[context.dataIndex];
                const lines = [
                  `LST: ${obs.lst}°C`,
                  `NDVI: ${obs.ndvi}`,
                  `Predicted: ${obs.predictedLst}°C`,
                ];
                if (obs.locationName) lines.unshift(obs.locationName);
                if (obs.surfaceType) lines.push(`Surface: ${obs.surfaceType}`);
                return lines;
              }
              const pt = context.raw;
              return `Predicted LST: ${pt.y}°C at NDVI ${pt.x}`;
            },
          },
        },
      },
      scales: {
        x: {
          title: {
            display: true,
            text: "NDVI (vegetation density)",
            color: "#94a3b8",
            font: { family: "Instrument Sans", size: 12 },
          },
          grid: { color: "rgba(255,255,255,0.06)" },
          ticks: { color: "#94a3b8" },
        },
        y: {
          title: {
            display: true,
            text: "Land surface temperature (°C)",
            color: "#94a3b8",
            font: { family: "Instrument Sans", size: 12 },
          },
          grid: { color: "rgba(255,255,255,0.06)" },
          ticks: { color: "#94a3b8" },
        },
      },
    },
  });
}

function updateChart(data) {
  regChart.data.datasets[0].data = data.observations.map((o) => ({
    x: o.ndvi,
    y: o.lst,
  }));
  regChart.data.datasets[1].data = data.regressionLine.map((p) => ({
    x: p.ndvi,
    y: p.predictedLst,
  }));
  regChart.update("active");
}

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
