/**
 * Decision Support Center — Strategic action cards for policymakers
 */

const REGIONS = "mirpur12,dhaka_all,sylhet,rajshahi,chittagong";

const CATEGORY_LABELS = {
  urban_forestry: "Urban forestry",
  public_green_space: "Public green space",
  surface_cooling: "Surface cooling",
  building_greening: "Building greening",
};

const PRIORITY_RANK = { Critical: 4, High: 3, Medium: 2, Low: 1 };

let allActions = [];
let filters = {
  region: "all",
  priority: "all",
  category: "all",
  sort: "priority",
};

document.addEventListener("DOMContentLoaded", () => {
  bindFilters();
  loadDecisionSupport();
});

function bindFilters() {
  document.getElementById("filter-region").addEventListener("change", (e) => {
    filters.region = e.target.value;
    renderCards();
  });

  document.getElementById("filter-category").addEventListener("change", (e) => {
    filters.category = e.target.value;
    renderCards();
  });

  document.getElementById("filter-sort").addEventListener("change", (e) => {
    filters.sort = e.target.value;
    renderCards();
  });

  document.querySelectorAll("#filter-priority .dec-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll("#filter-priority .dec-chip").forEach((c) => c.classList.remove("is-active"));
      chip.classList.add("is-active");
      filters.priority = chip.dataset.priority;
      renderCards();
    });
  });
}

function setLoading(on) {
  document.body.classList.toggle("decisions-loading", on);
}

async function loadDecisionSupport() {
  setLoading(true);
  try {
    const res = await fetch(`/api/decision-support?regions=${REGIONS}`);
    if (!res.ok) throw new Error("EDSS API failure");
    const data = await res.json();

    allActions = flattenActions(data);
    populateBrief(data);
    renderCards();

    if (data.generatedAt) {
      document.getElementById("dec-generated").textContent =
        `Intelligence brief · ${new Date(data.generatedAt).toLocaleString()}`;
    }
  } catch (err) {
    console.error(err);
    document.getElementById("dec-executive-summary").textContent =
      "Unable to load decision support data. Ensure the backend is running on port 5000.";
  } finally {
    setLoading(false);
  }
}

function flattenActions(data) {
  const reports = data.reports || (data.policySuggestions ? [data] : []);
  const actions = [];

  reports.forEach((report) => {
    (report.policySuggestions || []).forEach((policy) => {
      actions.push({
        ...policy,
        regionId: report.region,
        regionName: report.name,
        metrics: report.aggregatedMetrics,
      });
    });
  });

  return actions;
}

function populateBrief(data) {
  const reports = data.reports || [];
  const critical = allActions.filter((a) => a.priority === "Critical").length;
  const high = allActions.filter((a) => a.priority === "High").length;
  const avgCooling = allActions.length
    ? (allActions.reduce((s, a) => s + (a.estimatedCoolingEffectC || 0), 0) / allActions.length).toFixed(2)
    : "—";

  const summaries = reports
    .map((r) => r.humanReadableRecommendations?.executiveSummary)
    .filter(Boolean);

  document.getElementById("dec-executive-summary").textContent = summaries.length
    ? summaries[0] + (summaries.length > 1 ? ` Analysis covers ${reports.length} jurisdictions with ${allActions.length} strategic actions identified.` : "")
    : "Environmental decision support analysis complete.";

  document.getElementById("dec-brief-stats").innerHTML = `
    <div class="dec-brief-stat">
      <span class="dec-brief-stat__label">Critical actions</span>
      <span class="dec-brief-stat__value" style="color:var(--heat-extreme)">${critical}</span>
    </div>
    <div class="dec-brief-stat">
      <span class="dec-brief-stat__label">High priority</span>
      <span class="dec-brief-stat__value" style="color:var(--heat-high)">${high}</span>
    </div>
    <div class="dec-brief-stat">
      <span class="dec-brief-stat__label">Avg cooling potential</span>
      <span class="dec-brief-stat__value" style="color:#38bdf8">−${avgCooling}°C</span>
    </div>
  `;
}

function getFilteredActions() {
  let list = [...allActions];

  if (filters.region !== "all") {
    list = list.filter((a) => a.regionId === filters.region);
  }
  if (filters.priority !== "all") {
    list = list.filter((a) => a.priority === filters.priority);
  }
  if (filters.category !== "all") {
    list = list.filter((a) => a.category === filters.category);
  }

  list.sort((a, b) => {
    switch (filters.sort) {
      case "cooling":
        return (b.estimatedCoolingEffectC || 0) - (a.estimatedCoolingEffectC || 0);
      case "impact":
        return (b.estimatedImpactScore || 0) - (a.estimatedImpactScore || 0);
      case "difficulty":
        return (a.implementationDifficultyScore || 0) - (b.implementationDifficultyScore || 0);
      default:
        return (b.priorityRank || 0) - (a.priorityRank || 0) || (b.urgencyScore || 0) - (a.urgencyScore || 0);
    }
  });

  return list;
}

function renderCards() {
  const grid = document.getElementById("action-grid");
  const empty = document.getElementById("dec-empty");
  const filtered = getFilteredActions();

  document.getElementById("action-count").textContent = String(filtered.length);

  grid.querySelectorAll(".action-card").forEach((el) => el.remove());

  if (!filtered.length) {
    empty.hidden = false;
    return;
  }
  empty.hidden = true;

  filtered.forEach((action, index) => {
    const card = document.createElement("article");
    card.className = `action-card action-card--${action.priority}`;
    card.style.animationDelay = `${Math.min(index * 0.04, 0.4)}s`;

    card.innerHTML = `
      <div class="action-card__accent"></div>
      <div class="action-card__header">
        <span class="action-card__priority">${action.priority}</span>
        <span class="action-card__region">${escapeHtml(action.regionName)}</span>
      </div>
      <h3 class="action-card__title">${escapeHtml(action.title)}</h3>
      <p class="action-card__category">${CATEGORY_LABELS[action.category] || action.category}</p>
      <p class="action-card__rationale">${escapeHtml(action.rationale)}</p>
      <div class="action-card__metrics">
        <div class="action-card__metric">
          <span class="action-card__metric-label">Est. impact</span>
          <span class="action-card__metric-value action-card__metric-value--impact">${action.estimatedImpact || "—"}</span>
        </div>
        <div class="action-card__metric">
          <span class="action-card__metric-label">Cooling effect</span>
          <span class="action-card__metric-value action-card__metric-value--cool">−${action.estimatedCoolingEffectC ?? "—"}°C</span>
        </div>
        <div class="action-card__metric">
          <span class="action-card__metric-label">Difficulty</span>
          <span class="action-card__metric-value">${action.implementationDifficulty || "—"}</span>
        </div>
      </div>
      <div class="action-card__footer">
        <span>${escapeHtml(action.impactScope || "")}</span>
        <span class="difficulty-dots" title="Implementation difficulty: ${action.implementationDifficulty}">
          ${renderDifficultyDots(action.implementationDifficultyScore)}
        </span>
      </div>
    `;

    grid.appendChild(card);
  });
}

function renderDifficultyDots(score) {
  const s = score || 3;
  return Array.from({ length: 5 }, (_, i) =>
    `<span class="difficulty-dot${i < s ? " is-filled" : ""}"></span>`
  ).join("");
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
