/**
 * Premium Heat Risk visualization — gradient heatmaps, risk indicators,
 * clusters, summary panel, and hotspot detail drawer.
 */

const RISK_LEVELS = ["Very Low", "Low", "Moderate", "High", "Extreme"];

const RISK_LEVEL_CLASS = {
  "Very Low": "very-low",
  Low: "low",
  Moderate: "moderate",
  High: "high",
  Extreme: "extreme",
};

const HEAT_GRADIENT = {
  0.0: "#22c55e",
  0.25: "#84cc16",
  0.4: "#eab308",
  0.55: "#f97316",
  0.75: "#ef4444",
  1.0: "#991b1b",
};

class HeatRiskViz {
  constructor(mapEngine) {
    this.engine = mapEngine;
    this.map = mapEngine.map;
    this.colors = mapEngine.colors;
    this.wrapperId = mapEngine.wrapperId;
    this.heatmapLayer = null;
    this.clusterGroup = null;
    this.pulseLayer = null;
    this.summaryEl = null;
    this.detailEl = null;
    this.locations = [];
    this.isVisible = false;
    this._selectedMarker = null;
  }

  init() {
    this._createSummaryPanel();
    this._createDetailPanel();
  }

  setLocations(locations) {
    this.locations = locations || [];
    this._rebuild();
    this._updateSummary();
    if (this.isVisible) this.show();
  }

  show() {
    this.isVisible = true;
    if (this.heatmapLayer && !this.map.hasLayer(this.heatmapLayer)) {
      this.heatmapLayer.addTo(this.map);
    }
    if (this.clusterGroup && !this.map.hasLayer(this.clusterGroup)) {
      this.clusterGroup.addTo(this.map);
    }
    if (this.pulseLayer && !this.map.hasLayer(this.pulseLayer)) {
      this.pulseLayer.addTo(this.map);
    }
    this.summaryEl?.classList.add("is-visible");
    this.engine._updateLegend("heat-risk");
  }

  hide() {
    this.isVisible = false;
    if (this.heatmapLayer) this.map.removeLayer(this.heatmapLayer);
    if (this.clusterGroup) this.map.removeLayer(this.clusterGroup);
    if (this.pulseLayer) this.map.removeLayer(this.pulseLayer);
    this.summaryEl?.classList.remove("is-visible");
    this.closeDetail();
  }

  _rebuild() {
    this._destroyLayers();
    if (!this.locations.length || typeof L.heatLayer !== "function") return;

    const heatPoints = this.locations.map((loc) => [
      loc.lat,
      loc.lng,
      Math.max(0.08, loc.hri ?? this._estimateHri(loc)),
    ]);

    this.heatmapLayer = L.heatLayer(heatPoints, {
      radius: 42,
      blur: 28,
      maxZoom: 18,
      minOpacity: 0.35,
      max: 1.0,
      gradient: HEAT_GRADIENT,
    });

    this.clusterGroup = L.markerClusterGroup({
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      spiderfyOnMaxZoom: true,
      removeOutsideVisibleBounds: true,
      animate: true,
      animateAddingMarkers: false,
      maxClusterRadius: 52,
      iconCreateFunction: (cluster) => this._createClusterIcon(cluster),
    });

    this.pulseLayer = L.layerGroup();

    this.locations.forEach((loc) => {
      const level = loc.riskLevel || this._classifyRiskLevel(loc.hri);
      const levelClass = RISK_LEVEL_CLASS[level] || "moderate";
      const isHotspot = level === "High" || level === "Extreme";

      const marker = L.marker([loc.lat, loc.lng], {
        icon: this._createRiskIcon(loc, levelClass, isHotspot),
        locData: loc,
        riseOnHover: true,
      });

      marker.on("click", () => {
        this.openDetail(loc, marker);
      });

      this.clusterGroup.addLayer(marker);

      if (isHotspot) {
        const pulse = L.marker([loc.lat, loc.lng], {
          icon: L.divIcon({
            className: "risk-pulse-ring-wrapper",
            html: `<div class="risk-pulse-ring risk-pulse-ring--${levelClass}"></div>`,
            iconSize: [56, 56],
            iconAnchor: [28, 28],
          }),
          interactive: false,
        });
        this.pulseLayer.addLayer(pulse);
      }
    });
  }

  _destroyLayers() {
    if (this.heatmapLayer) {
      this.map.removeLayer(this.heatmapLayer);
      this.heatmapLayer = null;
    }
    if (this.clusterGroup) {
      this.map.removeLayer(this.clusterGroup);
      this.clusterGroup.clearLayers();
      this.clusterGroup = null;
    }
    if (this.pulseLayer) {
      this.map.removeLayer(this.pulseLayer);
      this.pulseLayer.clearLayers();
      this.pulseLayer = null;
    }
  }

  _estimateHri(loc) {
    const lst = loc.lst ?? 30;
    const ndvi = loc.ndvi ?? 0.3;
    const normLst = Math.min(1, Math.max(0, (lst - 10) / 55));
    const normNdvi = Math.min(1, Math.max(0, (ndvi + 0.3) / 1.1));
    return normLst * (1 - normNdvi);
  }

  _classifyRiskLevel(hri) {
    const h = hri ?? 0;
    if (h >= 0.8) return "Extreme";
    if (h >= 0.6) return "High";
    if (h >= 0.4) return "Moderate";
    if (h >= 0.2) return "Low";
    return "Very Low";
  }

  _createRiskIcon(loc, levelClass, isHotspot) {
    const hriPct = ((loc.hri ?? this._estimateHri(loc)) * 100).toFixed(0);
    const shortLevel = (loc.riskLevel || "—").split(" ")[0];

    return L.divIcon({
      className: "risk-pin-host",
      html: `
        <div class="risk-pin risk-pin--${levelClass}${isHotspot ? " risk-pin--pulse" : ""}">
          <div class="risk-pin__halo"></div>
          <div class="risk-pin__head">
            <span class="risk-pin__level">${this._escape(shortLevel)}</span>
            <span class="risk-pin__value">${hriPct}%</span>
          </div>
          <div class="risk-pin__needle"></div>
          <div class="risk-pin__dot"></div>
        </div>
      `,
      iconSize: [36, 46],
      iconAnchor: [18, 44],
    });
  }

  _createClusterIcon(cluster) {
    const markers = cluster.getAllChildMarkers();
    const count = cluster.getChildCount();
    let maxHri = 0;
    let dominantLevel = "moderate";

    markers.forEach((m) => {
      const hri = m.options.locData?.hri ?? 0;
      if (hri > maxHri) {
        maxHri = hri;
        dominantLevel = RISK_LEVEL_CLASS[this._classifyRiskLevel(hri)] || "moderate";
      }
    });

    return L.divIcon({
      html: `
        <div class="risk-cluster risk-cluster--${dominantLevel}">
          <span class="risk-cluster__count">${count}</span>
          <span class="risk-cluster__label">risk zone${count > 1 ? "s" : ""}</span>
        </div>
      `,
      className: "risk-cluster-host",
      iconSize: [48, 48],
      iconAnchor: [24, 24],
    });
  }

  _createSummaryPanel() {
    const wrapper = document.getElementById(this.wrapperId);
    if (!wrapper) return;

    this.summaryEl = document.createElement("aside");
    this.summaryEl.id = "risk-summary-panel";
    this.summaryEl.className = "risk-summary-panel";
    this.summaryEl.setAttribute("aria-label", "Heat risk summary");
    this.summaryEl.innerHTML = `
      <div class="risk-summary-panel__header">
        <span class="risk-summary-panel__eyebrow">Heat Risk Intelligence</span>
        <h3 class="risk-summary-panel__title">Regional summary</h3>
      </div>
      <div class="risk-summary-panel__hero">
        <div class="risk-summary-panel__avg">
          <span class="risk-summary-panel__avg-label">Mean HRI</span>
          <span class="risk-summary-panel__avg-value" id="risk-summary-avg">—</span>
        </div>
        <div class="risk-summary-panel__level" id="risk-summary-level">—</div>
      </div>
      <div class="risk-summary-panel__grid" id="risk-summary-grid"></div>
      <div class="risk-summary-panel__hotspots">
        <span class="risk-summary-panel__hotspots-title">Pulsing hotspots</span>
        <ul class="risk-summary-panel__hotspot-list" id="risk-summary-hotspots"></ul>
      </div>
    `;
    wrapper.appendChild(this.summaryEl);
  }

  _updateSummary() {
    if (!this.summaryEl || !this.locations.length) return;

    const hriValues = this.locations.map((l) => l.hri ?? this._estimateHri(l));
    const avgHri = hriValues.reduce((a, b) => a + b, 0) / hriValues.length;
    const avgLevel = this._classifyRiskLevel(avgHri);
    const levelClass = RISK_LEVEL_CLASS[avgLevel] || "moderate";

    const counts = { "Very Low": 0, Low: 0, Moderate: 0, High: 0, Extreme: 0 };
    this.locations.forEach((loc) => {
      const level = loc.riskLevel || this._classifyRiskLevel(loc.hri);
      if (counts[level] !== undefined) counts[level]++;
    });

    const avgEl = document.getElementById("risk-summary-avg");
    const levelEl = document.getElementById("risk-summary-level");
    const gridEl = document.getElementById("risk-summary-grid");
    const hotspotsEl = document.getElementById("risk-summary-hotspots");

    if (avgEl) {
      avgEl.textContent = `${(avgHri * 100).toFixed(1)}%`;
      avgEl.className = `risk-summary-panel__avg-value risk-summary-panel__avg-value--${levelClass}`;
    }
    if (levelEl) {
      levelEl.textContent = avgLevel;
      levelEl.className = `risk-summary-panel__level risk-summary-panel__level--${levelClass}`;
    }
    if (gridEl) {
      gridEl.innerHTML = RISK_LEVELS.map((level) => {
        const cls = RISK_LEVEL_CLASS[level];
        return `
          <div class="risk-summary-stat risk-summary-stat--${cls}">
            <span class="risk-summary-stat__count">${counts[level]}</span>
            <span class="risk-summary-stat__label">${level}</span>
          </div>`;
      }).join("");
    }
    if (hotspotsEl) {
      const top = [...this.locations]
        .sort((a, b) => (b.hri ?? 0) - (a.hri ?? 0))
        .slice(0, 3);
      hotspotsEl.innerHTML = top
        .map(
          (loc) => `
          <li>
            <button type="button" class="risk-summary-hotspot" data-lat="${loc.lat}" data-lng="${loc.lng}">
              <span class="risk-summary-hotspot__name">${this._escape(loc.name || "Point")}</span>
              <span class="risk-summary-hotspot__hri">${((loc.hri ?? 0) * 100).toFixed(0)}%</span>
            </button>
          </li>`
        )
        .join("");

      hotspotsEl.querySelectorAll(".risk-summary-hotspot").forEach((btn) => {
        btn.addEventListener("click", () => {
          const lat = parseFloat(btn.dataset.lat);
          const lng = parseFloat(btn.dataset.lng);
          const loc = this.locations.find(
            (l) => Math.abs(l.lat - lat) < 1e-5 && Math.abs(l.lng - lng) < 1e-5
          );
          if (loc) {
            this.map.flyTo([loc.lat, loc.lng], Math.max(this.map.getZoom(), 16), {
              duration: 1.2,
              easeLinearity: 0.25,
            });
            this.openDetail(loc);
          }
        });
      });
    }
  }

  _createDetailPanel() {
    const wrapper = document.getElementById(this.wrapperId);
    if (!wrapper) return;

    this.detailEl = document.createElement("aside");
    this.detailEl.id = "risk-detail-panel";
    this.detailEl.className = "risk-detail-panel";
    this.detailEl.setAttribute("aria-label", "Hotspot detail");
    this.detailEl.hidden = true;
    this.detailEl.innerHTML = `
      <button type="button" class="risk-detail-panel__close" aria-label="Close detail panel">&times;</button>
      <div class="risk-detail-panel__content" id="risk-detail-content"></div>
    `;
    wrapper.appendChild(this.detailEl);

    this.detailEl.querySelector(".risk-detail-panel__close").addEventListener("click", () => {
      this.closeDetail();
    });
  }

  openDetail(loc, marker) {
    if (!this.detailEl) return;

    const level = loc.riskLevel || this._classifyRiskLevel(loc.hri);
    const levelClass = RISK_LEVEL_CLASS[level] || "moderate";
    const hriPct = ((loc.hri ?? this._estimateHri(loc)) * 100).toFixed(1);
    const lstColor = this.engine._lstColor(loc.lst);

    const recHtml = loc.recommendation
      ? `
        <div class="risk-detail-rec">
          <h4>Recommendations</h4>
          <span class="risk-detail-rec__tier">${this._escape(loc.recommendation.interventionLevel)}</span>
          ${loc.recommendation.priorityArea ? '<span class="risk-detail-rec__priority">Priority area</span>' : ""}
          <ul>${(loc.recommendation.actions || []).map((a) => `<li>${this._escape(a)}</li>`).join("")}</ul>
        </div>`
      : `<div class="risk-detail-rec risk-detail-rec--empty"><p>No intervention recommendations for this location.</p></div>`;

    const content = document.getElementById("risk-detail-content");
    if (content) {
      content.innerHTML = `
        <div class="risk-detail-card risk-detail-card--${levelClass}">
          <div class="risk-detail-card__header">
            <div>
              <span class="risk-detail-card__eyebrow">Hotspot intelligence</span>
              <h3>${this._escape(loc.name || "Monitoring point")}</h3>
              <p class="risk-detail-card__coords">${loc.lat?.toFixed(5)}, ${loc.lng?.toFixed(5)}</p>
            </div>
            <span class="risk-detail-card__badge risk-detail-card__badge--${levelClass}">${this._escape(level)}</span>
          </div>
          ${
            loc.image
              ? `<div class="risk-detail-card__image"><img src="images/${this._escape(loc.image)}" alt="${this._escape(loc.name)}" loading="lazy" onerror="this.closest('.risk-detail-card__image').innerHTML='<span class=\\'env-popup__image-fallback\\'>Ground photo unavailable</span>'"/></div>`
              : ""
          }
          <div class="risk-detail-card__metrics">
            <div class="risk-detail-metric">
              <span class="risk-detail-metric__icon">🌡</span>
              <div>
                <span class="risk-detail-metric__label">Temperature</span>
                <span class="risk-detail-metric__value" style="color:${lstColor}">${loc.lst ?? "—"}°C</span>
              </div>
            </div>
            <div class="risk-detail-metric">
              <span class="risk-detail-metric__icon">🌿</span>
              <div>
                <span class="risk-detail-metric__label">NDVI</span>
                <span class="risk-detail-metric__value">${loc.ndvi ?? "—"}</span>
              </div>
            </div>
            <div class="risk-detail-metric">
              <span class="risk-detail-metric__icon">☀</span>
              <div>
                <span class="risk-detail-metric__label">Heat Risk Index</span>
                <span class="risk-detail-metric__value">${hriPct}%</span>
              </div>
            </div>
            <div class="risk-detail-metric">
              <span class="risk-detail-metric__icon">🛡</span>
              <div>
                <span class="risk-detail-metric__label">Climate Score</span>
                <span class="risk-detail-metric__value">${loc.climateScore != null ? Math.round(loc.climateScore) + "/100" : "—"}</span>
              </div>
            </div>
          </div>
          <div class="risk-detail-card__meta">
            <span><strong>Surface</strong> ${this._escape(loc.surface || "—")}</span>
            <span><strong>Resilience</strong> ${this._escape(loc.climateCategory || "—")}</span>
          </div>
          ${recHtml}
        </div>
      `;
    }

    this.detailEl.hidden = false;
    requestAnimationFrame(() => this.detailEl.classList.add("is-open"));

    if (marker) {
      this._selectedMarker = marker;
    }

    this.map.flyTo([loc.lat, loc.lng], Math.max(this.map.getZoom(), 16), {
      duration: 1.0,
      easeLinearity: 0.25,
    });
  }

  closeDetail() {
    if (!this.detailEl) return;
    this.detailEl.classList.remove("is-open");
    this._selectedMarker = null;
    setTimeout(() => {
      this.detailEl.hidden = true;
    }, 280);
  }

  renderGradientLegend(legendEl) {
    if (!legendEl) return;
    legendEl.innerHTML = `
      <div class="legend-title">Heat Risk gradient</div>
      <div class="legend-gradient-bar" aria-hidden="true"></div>
      <div class="legend-gradient-labels">
        <span>Low</span>
        <span>Moderate</span>
        <span>High</span>
        <span>Extreme</span>
      </div>
      <div class="legend-divider"></div>
      <div class="legend-title">Risk indicators</div>
      <div class="legend-item"><div class="legend-pin legend-pin--extreme"></div><span>Extreme (≥80%)</span></div>
      <div class="legend-item"><div class="legend-pin legend-pin--high"></div><span>High (60–80%)</span></div>
      <div class="legend-item"><div class="legend-pin legend-pin--moderate"></div><span>Moderate (40–60%)</span></div>
      <div class="legend-item"><div class="legend-pin legend-pin--low"></div><span>Low / Very Low</span></div>
      <div class="legend-item"><div class="legend-pulse-demo"></div><span>Pulsing hotspot</span></div>
      <div class="legend-item"><div class="legend-cluster-demo">3</div><span>Risk cluster</span></div>
    `;
  }

  _escape(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
}

window.HeatRiskViz = HeatRiskViz;
