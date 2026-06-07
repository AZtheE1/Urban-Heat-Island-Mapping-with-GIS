/**
 * Report Studio — Enterprise environmental report builder
 */

const REGIONS = [
  { id: "dhaka_all", name: "Dhaka Metropolitan Area" },
  { id: "mirpur12", name: "Mirpur 12" },
  { id: "sylhet", name: "Sylhet Division" },
  { id: "rajshahi", name: "Rajshahi Division" },
  { id: "chittagong", name: "Chittagong Division" },
];

const TEMPLATES = [
  {
    id: "executive",
    name: "Executive Brief",
    subtitle: "Cabinet-level summary for senior officials",
    badge: "Official",
    title: "Executive Environmental Intelligence Brief",
    classification: "OFFICIAL — LIMITED DISTRIBUTION",
    modules: ["temperature", "climate", "recommendations"],
  },
  {
    id: "full",
    name: "Full Environmental Assessment",
    subtitle: "Comprehensive technical environmental report",
    badge: "Standard",
    title: "Comprehensive Urban Heat Island Environmental Assessment",
    classification: "OFFICIAL — TECHNICAL REPORT",
    modules: ["temperature", "ndvi", "heatRisk", "climate", "recommendations"],
  },
  {
    id: "multi",
    name: "Multi-Jurisdiction Comparison",
    subtitle: "Cross-city comparative intelligence document",
    badge: "Comparative",
    title: "Multi-Jurisdiction Environmental Comparison Report",
    classification: "OFFICIAL — INTER-DIVISIONAL",
    modules: ["temperature", "ndvi", "heatRisk", "climate"],
  },
  {
    id: "heatRisk",
    name: "Heat Risk Focus",
    subtitle: "Heat exposure and mitigation priority report",
    badge: "Priority",
    title: "Heat Risk & Mitigation Priority Report",
    classification: "OFFICIAL — HEAT ACTION",
    modules: ["temperature", "heatRisk", "recommendations"],
  },
];

let selectedTemplate = TEMPLATES[1];
let reportData = null;
let selectedRegions = new Set(["mirpur12"]);

document.addEventListener("DOMContentLoaded", () => {
  buildTemplates();
  buildRegions();
  bindEvents();
  setExportStep("configure", "complete", "Template & regions ready");
});

function buildTemplates() {
  const grid = document.getElementById("template-grid");
  TEMPLATES.forEach((tpl) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `template-card${tpl.id === selectedTemplate.id ? " is-selected" : ""}`;
    btn.dataset.id = tpl.id;
    btn.setAttribute("role", "radio");
    btn.setAttribute("aria-checked", tpl.id === selectedTemplate.id ? "true" : "false");
    btn.innerHTML = `
      <span class="template-card__badge">${tpl.badge}</span>
      <span class="template-card__name">${tpl.name}</span>
      <span class="template-card__sub">${tpl.subtitle}</span>
    `;
    btn.addEventListener("click", () => selectTemplate(tpl.id));
    grid.appendChild(btn);
  });
}

function selectTemplate(id) {
  selectedTemplate = TEMPLATES.find((t) => t.id === id) || TEMPLATES[1];
  document.querySelectorAll(".template-card").forEach((card) => {
    const isSel = card.dataset.id === id;
    card.classList.toggle("is-selected", isSel);
    card.setAttribute("aria-checked", isSel ? "true" : "false");
  });
  applyTemplateModules();
}

function applyTemplateModules() {
  const modules = new Set(selectedTemplate.modules);
  document.querySelectorAll("#module-checklist input").forEach((input) => {
    input.checked = modules.has(input.value);
  });
}

function buildRegions() {
  const list = document.getElementById("region-checklist");
  REGIONS.forEach((r) => {
    const label = document.createElement("label");
    label.className = "region-check";
    label.innerHTML = `
      <input type="checkbox" value="${r.id}" ${selectedRegions.has(r.id) ? "checked" : ""} />
      ${r.name}
    `;
    label.querySelector("input").addEventListener("change", (e) => {
      if (e.target.checked) selectedRegions.add(r.id);
      else {
        if (selectedRegions.size <= 1) {
          e.target.checked = true;
          return;
        }
        selectedRegions.delete(r.id);
      }
    });
    list.appendChild(label);
  });
}

function getSelectedModules() {
  return new Set(
    [...document.querySelectorAll("#module-checklist input:checked")].map((i) => i.value)
  );
}

function bindEvents() {
  document.getElementById("btn-generate").addEventListener("click", generatePreview);
  document.getElementById("select-all-regions").addEventListener("click", () => {
    selectedRegions = new Set(REGIONS.map((r) => r.id));
    document.querySelectorAll("#region-checklist input").forEach((i) => { i.checked = true; });
  });
  document.getElementById("btn-export-pdf").addEventListener("click", exportPdf);
  document.getElementById("btn-export-json").addEventListener("click", exportJson);
}

function getRegionsParam() {
  return [...selectedRegions].join(",");
}

function setLoading(on, msg) {
  document.body.classList.toggle("reports-loading", on);
  if (msg) document.getElementById("loader-message").textContent = msg;
}

function setExportStep(step, state, message) {
  const el = document.querySelector(`.export-step[data-step="${step}"]`);
  if (!el) return;
  el.classList.remove("is-active", "is-complete", "is-error");
  if (state) el.classList.add(`is-${state}`);
  const msgEl = el.querySelector("span:last-child");
  if (msgEl && message) msgEl.textContent = message;

  if (step === "generate" && message) {
    document.getElementById("status-generate").textContent = message;
  }
  if (step === "export" && message) {
    document.getElementById("status-export").textContent = message;
  }
}

function setPreviewStatus(text, state) {
  const badge = document.getElementById("preview-status");
  badge.textContent = text;
  badge.className = "preview-badge" + (state ? ` is-${state}` : "");
}

async function generatePreview() {
  const regions = getRegionsParam();
  if (!regions) return;

  setLoading(true, "Generating environmental report preview…");
  setPreviewStatus("Generating…", "generating");
  setExportStep("generate", "active", "Compiling report data…");
  document.getElementById("btn-generate").disabled = true;

  try {
    const res = await fetch(`/api/report?regions=${regions}&format=json`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || "Report generation failed");
    }
    reportData = await res.json();
    renderPreview(reportData);
    updateExportInfo(reportData);
    enableExports();

    setPreviewStatus("Preview ready", "ready");
    setExportStep("generate", "complete", `Report compiled · ${reportData.sectionCount} sections`);
    setExportStep("export", "active", "Ready for download");
    document.getElementById("preview-meta").textContent =
      `${reportData.reportId} · ${new Date(reportData.generatedAt).toLocaleString()}`;
  } catch (err) {
    console.error(err);
    setPreviewStatus("Generation failed", "");
    setExportStep("generate", "error", err.message);
  } finally {
    setLoading(false);
    document.getElementById("btn-generate").disabled = false;
  }
}

function renderPreview(data) {
  document.getElementById("preview-placeholder").hidden = true;
  const report = document.getElementById("gov-report");
  report.hidden = false;

  const modules = getSelectedModules();
  const tpl = selectedTemplate;

  let bodyHtml = "";

  if (tpl.id === "executive") {
    bodyHtml += renderExecutiveSummary(data);
  }

  data.sections.forEach((section, idx) => {
    bodyHtml += `<div class="gov-report__section">`;
    bodyHtml += `<h3 class="gov-report__section-title">Section ${idx + 1} — Regional Analysis</h3>`;
    bodyHtml += `<p class="gov-report__region-name">${escapeHtml(section.name)}</p>`;
    if (section.description) {
      bodyHtml += `<p class="gov-report__desc">${escapeHtml(section.description)}</p>`;
    }

    if (modules.has("temperature") && section.temperatureStatistics) {
      bodyHtml += renderTempTable(section.temperatureStatistics);
    }
    if (modules.has("ndvi") && section.ndviStatistics) {
      bodyHtml += renderNdviTable(section.ndviStatistics);
    }
    if (modules.has("heatRisk") && section.heatRiskIndex) {
      bodyHtml += renderHeatRiskSection(section.heatRiskIndex);
    }
    if (modules.has("climate") && section.climateScore) {
      bodyHtml += renderClimateSection(section.climateScore);
    }
    if (modules.has("recommendations") && section.recommendations) {
      bodyHtml += renderRecommendationsSection(section.recommendations);
    }

    bodyHtml += `</div>`;
  });

  report.innerHTML = `
    <header class="gov-report__letterhead">
      <div class="gov-report__emblem" aria-hidden="true">🇧🇩</div>
      <p class="gov-report__republic">People's Republic of Bangladesh</p>
      <p class="gov-report__ministry">Ministry of Environment · Urban Heat Island Intelligence Programme</p>
      <h1 class="gov-report__title">${escapeHtml(tpl.title)}</h1>
      <p class="gov-report__subtitle">${escapeHtml(tpl.subtitle)}</p>
    </header>
    <div class="gov-report__meta-bar">
      <span><strong>Report ID:</strong> ${escapeHtml(data.reportId)}</span>
      <span><strong>Generated:</strong> ${new Date(data.generatedAt).toLocaleString()}</span>
      <span><strong>Regions:</strong> ${data.regions.length}</span>
      <span><strong>Template:</strong> ${escapeHtml(tpl.name)}</span>
    </div>
    <div class="gov-report__body">${bodyHtml}</div>
    <footer class="gov-report__footer">
      <div class="gov-report__classification">${escapeHtml(tpl.classification)}</div>
      <p>Automated environmental intelligence report · Environmental Decision Support System</p>
      <p>This document was generated by the Urban Heat Island Mapping &amp; Analytics System.</p>
    </footer>
  `;
}

function renderExecutiveSummary(data) {
  const sections = data.sections || [];
  const avgTemp = sections.reduce((s, r) => s + (r.temperatureStatistics?.mean || 0), 0) / sections.length;
  const avgScore = sections.reduce((s, r) => s + (r.climateScore?.score || 0), 0) / sections.length;

  return `
    <div class="gov-report__section">
      <h3 class="gov-report__section-title">Executive Summary</h3>
      <p class="gov-report__desc" style="font-family:var(--font-body)">
        This ${selectedTemplate.name.toLowerCase()} covers <strong>${sections.length}</strong> jurisdiction(s)
        with a mean land surface temperature of <strong>${avgTemp.toFixed(2)}°C</strong> and average climate
        resilience score of <strong>${avgScore.toFixed(1)}/100</strong>. Priority green infrastructure
        interventions are recommended for high heat-exposure zones identified in the heat risk analysis.
      </p>
    </div>`;
}

function renderTempTable(stats) {
  return `
    <table class="gov-table">
      <caption style="caption-side:top;text-align:left;font-weight:700;font-size:0.75rem;margin-bottom:8px;color:#44403c">
        Land Surface Temperature (°C)
      </caption>
      <thead><tr><th>Metric</th><th>Value</th></tr></thead>
      <tbody>
        <tr><td>Mean</td><td>${stats.mean}</td></tr>
        <tr><td>Maximum</td><td>${stats.max}</td></tr>
        <tr><td>Minimum</td><td>${stats.min}</td></tr>
        <tr><td>Std. deviation</td><td>${stats.std}</td></tr>
      </tbody>
    </table>`;
}

function renderNdviTable(stats) {
  return `
    <table class="gov-table">
      <caption style="caption-side:top;text-align:left;font-weight:700;font-size:0.75rem;margin-bottom:8px;color:#44403c">
        Normalized Difference Vegetation Index
      </caption>
      <thead><tr><th>Metric</th><th>Value</th></tr></thead>
      <tbody>
        <tr><td>Mean</td><td>${stats.mean}</td></tr>
        <tr><td>Maximum</td><td>${stats.max}</td></tr>
        <tr><td>Minimum</td><td>${stats.min}</td></tr>
      </tbody>
    </table>`;
}

function renderHeatRiskSection(hri) {
  const dist = hri.riskLevelDistribution || {};
  const rows = Object.entries(dist)
    .map(([level, count]) => `<tr><td>${escapeHtml(level)}</td><td>${count}</td></tr>`)
    .join("");
  return `
    <table class="gov-table">
      <caption style="caption-side:top;text-align:left;font-weight:700;font-size:0.75rem;margin-bottom:8px;color:#44403c">
        Heat Risk Index — Average: ${hri.average}
      </caption>
      <thead><tr><th>Risk level</th><th>Locations</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

function renderClimateSection(climate) {
  return `
    <table class="gov-table">
      <caption style="caption-side:top;text-align:left;font-weight:700;font-size:0.75rem;margin-bottom:8px;color:#44403c">
        Climate Resilience Assessment
      </caption>
      <thead><tr><th>Indicator</th><th>Value</th></tr></thead>
      <tbody>
        <tr><td>Resilience score</td><td>${climate.score}/100</td></tr>
        <tr><td>Category</td><td>${escapeHtml(climate.category)}</td></tr>
        <tr><td>Green coverage</td><td>${climate.summary?.greenCoveragePercentage ?? "—"}%</td></tr>
      </tbody>
    </table>`;
}

function renderRecommendationsSection(rec) {
  const items = (rec.items || []).slice(0, 5);
  const rows = items
    .map(
      (item) =>
        `<tr><td>${escapeHtml(item.locationName || "—")}</td><td>${escapeHtml(item.interventionLevel || "—")}</td><td>${item.vegetationDeficitScore ?? "—"}</td></tr>`
    )
    .join("");
  return `
    <table class="gov-table">
      <caption style="caption-side:top;text-align:left;font-weight:700;font-size:0.75rem;margin-bottom:8px;color:#44403c">
        Green Infrastructure Recommendations (${rec.summary?.priorityAreas ?? 0} priority areas)
      </caption>
      <thead><tr><th>Location</th><th>Intervention</th><th>Deficit score</th></tr></thead>
      <tbody>${rows || "<tr><td colspan='3'>No recommendations</td></tr>"}</tbody>
    </table>`;
}

function updateExportInfo(data) {
  document.getElementById("export-report-id").textContent = data.reportId;
  document.getElementById("export-timestamp").textContent = new Date(data.generatedAt).toLocaleString();
  document.getElementById("export-regions").textContent = data.regions.join(", ");
}

function enableExports() {
  document.getElementById("btn-export-pdf").disabled = false;
  document.getElementById("btn-export-json").disabled = false;
}

async function exportPdf() {
  const btn = document.getElementById("btn-export-pdf");
  const status = document.getElementById("pdf-status");
  btn.classList.add("is-exporting");
  status.textContent = "Exporting…";
  setExportStep("export", "active", "Generating PDF document…");
  setLoading(true, "Rendering PDF export…");

  try {
    const res = await fetch(`/api/report?regions=${getRegionsParam()}&format=pdf`);
    if (!res.ok) throw new Error("PDF export failed");
    const blob = await res.blob();
    downloadBlob(blob, `${reportData?.reportId || "environmental-report"}.pdf`);
    btn.classList.remove("is-exporting");
    btn.classList.add("is-success");
    status.textContent = "Complete";
    setExportStep("export", "complete", "PDF downloaded successfully");
  } catch (err) {
    console.error(err);
    btn.classList.remove("is-exporting");
    status.textContent = "Failed";
    setExportStep("export", "error", "PDF export failed");
  } finally {
    setLoading(false);
  }
}

function exportJson() {
  if (!reportData) return;
  const btn = document.getElementById("btn-export-json");
  const status = document.getElementById("json-status");
  status.textContent = "Exporting…";
  btn.classList.add("is-exporting");

  const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: "application/json" });
  downloadBlob(blob, `${reportData.reportId}.json`);

  btn.classList.remove("is-exporting");
  btn.classList.add("is-success");
  status.textContent = "Complete";
  setExportStep("export", "complete", "JSON downloaded successfully");
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
