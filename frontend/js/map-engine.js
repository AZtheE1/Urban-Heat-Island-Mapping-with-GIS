/**
 * Environmental Command Center — Leaflet Map Engine
 * Layered thematic visualization with performance-optimized marker groups.
 */

const MAP_LAYERS = {
  lst: {
    id: "lst",
    label: "LST",
    subtitle: "Land surface temperature",
    icon: "🌡",
  },
  ndvi: {
    id: "ndvi",
    label: "NDVI",
    subtitle: "Vegetation density index",
    icon: "🌿",
  },
  "heat-risk": {
    id: "heat-risk",
    label: "Heat Risk",
    subtitle: "Composite heat exposure",
    icon: "☀",
  },
  "climate-score": {
    id: "climate-score",
    label: "Climate Score",
    subtitle: "Resilience composite",
    icon: "🛡",
  },
  recommendations: {
    id: "recommendations",
    label: "Recommendations",
    subtitle: "Green infrastructure priority",
    icon: "📍",
  },
  alerts: {
    id: "alerts",
    label: "Alerts",
    subtitle: "Heatwave threshold status",
    icon: "🔔",
  },
};

const LAYER_LEGENDS = {
  lst: [
    { class: "legend-extreme", label: "Extreme (≥35°C)" },
    { class: "legend-high", label: "High (32–34°C)" },
    { class: "legend-moderate", label: "Moderate (30–31°C)" },
    { class: "legend-vegetation", label: "Cool (≤30°C)" },
  ],
  ndvi: [
    { class: "legend-vegetation", label: "Dense canopy (≥0.6)" },
    { class: "legend-moderate", label: "Moderate (0.3–0.6)" },
    { class: "legend-high", label: "Sparse (0.1–0.3)" },
    { class: "legend-extreme", label: "Bare surface (<0.1)" },
  ],
  "heat-risk": [
    { class: "legend-extreme", label: "Extreme (≥80%)" },
    { class: "legend-high", label: "High (60–80%)" },
    { class: "legend-moderate", label: "Moderate (40–60%)" },
    { class: "legend-vegetation", label: "Low (<40%)" },
  ],
  "climate-score": [
    { class: "legend-vegetation", label: "Excellent (81–100)" },
    { class: "legend-moderate", label: "Good / Moderate (41–80)" },
    { class: "legend-high", label: "Poor (21–40)" },
    { class: "legend-extreme", label: "Critical (0–20)" },
  ],
  recommendations: [
    { class: "legend-extreme", label: "Aggressive intervention" },
    { class: "legend-high", label: "Moderate intervention" },
    { class: "legend-vegetation", label: "Small intervention" },
    { class: "legend-moderate", label: "Priority area marker" },
  ],
  alerts: [
    { class: "legend-extreme", label: "Extreme (>40°C)" },
    { class: "legend-high", label: "Severe (>38°C)" },
    { class: "legend-moderate", label: "Warning (>35°C)" },
    { class: "legend-vegetation", label: "Normal" },
  ],
};

class MapEngine {
  constructor(options = {}) {
    this.options = options;
    this.containerId = options.containerId || "map-container";
    this.wrapperId = options.wrapperId || "map-wrapper";
    this.colors = options.colors || {};
    this.enabledLayers = options.enabledLayers || Object.keys(MAP_LAYERS);
    this.activeLayer =
      options.defaultLayer && this.enabledLayers.includes(options.defaultLayer)
        ? options.defaultLayer
        : this.enabledLayers.includes("heat-risk")
          ? "heat-risk"
          : this.enabledLayers[0] || "lst";
    this.map = null;
    this.miniMap = null;
    this.layerGroups = {};
    this.geojsonLayer = null;
    this.userGeojsonLayer = null;
    this.heatRiskViz = null;
    this.locations = [];
    this.regionCoords = null;
    this.isTransitioning = false;
    this._miniSyncing = false;
  }

  init() {
    this.map = L.map(this.containerId, {
      zoomControl: false,
      attributionControl: true,
      preferCanvas: true,
      fadeAnimation: true,
      zoomAnimation: true,
    }).setView([23.8243, 90.3653], 15);

    this.baseLayer = L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
      {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: "abcd",
        maxZoom: 20,
      }
    ).addTo(this.map);

    Object.keys(MAP_LAYERS).forEach((id) => {
      this.layerGroups[id] = L.layerGroup();
    });

    if (window.HeatRiskViz && this.enabledLayers.includes("heat-risk")) {
      this.heatRiskViz = new HeatRiskViz(this);
      this.heatRiskViz.init();
    }

    this._initControls();
    this._updateLegend(this.activeLayer);
  }

  _initControls() {
    this._createLayerPanel();
    this._createFloatingControls();
    this._createMinimap();
  }

  _createLayerPanel() {
    const LayerPanel = L.Control.extend({
      options: { position: "topleft" },
      onAdd: () => {
        const container = L.DomUtil.create("div", "map-layer-panel leaflet-control");
        container.innerHTML = `
          <div class="map-layer-panel__header">
            <span class="map-layer-panel__title">Environmental Layers</span>
            <span class="map-layer-panel__badge">GIS</span>
          </div>
          <div class="map-layer-panel__list" role="radiogroup" aria-label="Map data layers"></div>
        `;

        const list = container.querySelector(".map-layer-panel__list");
        Object.values(MAP_LAYERS)
          .filter((layer) => this.enabledLayers.includes(layer.id))
          .forEach((layer) => {
          const btn = L.DomUtil.create("button", "map-layer-option", list);
          btn.type = "button";
          btn.dataset.layer = layer.id;
          btn.setAttribute("role", "radio");
          btn.setAttribute("aria-checked", layer.id === this.activeLayer ? "true" : "false");
          btn.innerHTML = `
            <span class="map-layer-option__icon" aria-hidden="true">${layer.icon}</span>
            <span class="map-layer-option__text">
              <span class="map-layer-option__label">${layer.label}</span>
              <span class="map-layer-option__sub">${layer.subtitle}</span>
            </span>
            <span class="map-layer-option__indicator" aria-hidden="true"></span>
          `;
          if (layer.id === this.activeLayer) btn.classList.add("is-active");

          L.DomEvent.on(btn, "click", (e) => {
            L.DomEvent.stopPropagation(e);
            L.DomEvent.preventDefault(e);
            this.switchLayer(layer.id);
          });
        });

        L.DomEvent.disableClickPropagation(container);
        L.DomEvent.disableScrollPropagation(container);
        this.layerPanelEl = container;
        return container;
      },
    });

    new LayerPanel().addTo(this.map);
  }

  _createFloatingControls() {
    const FloatingControls = L.Control.extend({
      options: { position: "topright" },
      onAdd: () => {
        const container = L.DomUtil.create("div", "map-floating-controls leaflet-control");
        container.innerHTML = `
          <button type="button" class="map-ctrl-btn" data-action="zoom-in" title="Zoom in" aria-label="Zoom in">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </button>
          <button type="button" class="map-ctrl-btn" data-action="zoom-out" title="Zoom out" aria-label="Zoom out">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </button>
          <button type="button" class="map-ctrl-btn" data-action="recenter" title="Recenter region" aria-label="Recenter region">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>
          </button>
          <button type="button" class="map-ctrl-btn" data-action="fullscreen" title="Fullscreen" aria-label="Toggle fullscreen">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
          </button>
        `;

        container.querySelector('[data-action="zoom-in"]').addEventListener("click", (e) => {
          e.stopPropagation();
          this.map.zoomIn();
        });
        container.querySelector('[data-action="zoom-out"]').addEventListener("click", (e) => {
          e.stopPropagation();
          this.map.zoomOut();
        });
        container.querySelector('[data-action="recenter"]').addEventListener("click", (e) => {
          e.stopPropagation();
          this.flyToRegion(this.regionCoords);
        });
        container.querySelector('[data-action="fullscreen"]').addEventListener("click", (e) => {
          e.stopPropagation();
          this.toggleFullscreen();
        });

        L.DomEvent.disableClickPropagation(container);
        this.floatingControlsEl = container;
        return container;
      },
    });

    new FloatingControls().addTo(this.map);
  }

  _createMinimap() {
    const MiniMapControl = L.Control.extend({
      options: { position: "bottomleft" },
      onAdd: () => {
        const container = L.DomUtil.create("div", "map-minimap leaflet-control");
        const mapEl = L.DomUtil.create("div", "map-minimap__map", container);
        const label = L.DomUtil.create("span", "map-minimap__label", container);
        label.textContent = "Overview";

        this.miniMap = L.map(mapEl, {
          zoomControl: false,
          attributionControl: false,
          dragging: false,
          scrollWheelZoom: false,
          doubleClickZoom: false,
          boxZoom: false,
          keyboard: false,
          tap: false,
          touchZoom: false,
        });

        L.tileLayer(
          "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
          { subdomains: "abcd", maxZoom: 18 }
        ).addTo(this.miniMap);

        this.miniViewport = L.rectangle([[0, 0], [0, 0]], {
          color: "#38bdf8",
          weight: 2,
          fillColor: "#38bdf8",
          fillOpacity: 0.12,
          interactive: false,
        }).addTo(this.miniMap);

        this.map.on("moveend zoomend", () => this._syncMinimap());
        L.DomEvent.disableClickPropagation(container);
        L.DomEvent.disableScrollPropagation(container);
        return container;
      },
    });

    new MiniMapControl().addTo(this.map);
  }

  _syncMinimap() {
    if (!this.miniMap || this._miniSyncing) return;
    const bounds = this.map.getBounds();
    this.miniViewport.setBounds(bounds);

    if (this.regionCoords?.bounds) {
      this.miniMap.fitBounds(this.regionCoords.bounds, { animate: false });
    } else {
      this.miniMap.fitBounds(bounds.pad(0.4), { animate: false });
    }
  }

  toggleFullscreen() {
    const wrapper = document.getElementById(this.wrapperId);
    if (!wrapper) return;

    if (!document.fullscreenElement) {
      wrapper.requestFullscreen?.().then(() => {
        wrapper.classList.add("is-fullscreen");
        setTimeout(() => this.map.invalidateSize(), 200);
      });
    } else {
      document.exitFullscreen?.().then(() => {
        wrapper.classList.remove("is-fullscreen");
        setTimeout(() => this.map.invalidateSize(), 200);
      });
    }
  }

  flyToRegion(coords, options = {}) {
    if (!this.map || !coords) return;
    this.regionCoords = coords;
    this.map.flyTo(coords.center, coords.zoom, {
      animate: true,
      duration: options.duration || 1.6,
      easeLinearity: 0.22,
    });
    setTimeout(() => this._syncMinimap(), 1700);
  }

  setData({ records, risk, climate, recommendations, alerts, coords }) {
    this.regionCoords = coords;
    this.locations = this._mergeLocations(records, risk, climate, recommendations, alerts);
    this._buildAllLayers();
    if (this.heatRiskViz) {
      this.heatRiskViz.setLocations(this.locations);
    }
    this._attachActiveLayer();
    this._renderGeojson(coords);
    this._syncMinimap();
  }

  _attachActiveLayer() {
    Object.values(this.layerGroups).forEach((group) => {
      if (this.map.hasLayer(group)) this.map.removeLayer(group);
    });
    this.heatRiskViz?.hide();

    if (this.activeLayer === "heat-risk" && this.heatRiskViz) {
      this.heatRiskViz.show();
    } else {
      this.layerGroups[this.activeLayer].addTo(this.map);
    }
  }

  _coordKey(lat, lng) {
    return `${Number(lat).toFixed(6)},${Number(lng).toFixed(6)}`;
  }

  _mergeLocations(records, risk, climate, recommendations) {
    const index = new Map();

    (records || []).forEach((point) => {
      const key = this._coordKey(point.Latitude, point.Longitude);
      index.set(key, {
        name: point.LocationName,
        lat: point.Latitude,
        lng: point.Longitude,
        lst: point.Temperature,
        ndvi: point.NDVI ?? point.Calculated_NDVI,
        surface: point.SurfaceType,
        traffic: point.TrafficDensity,
        image: point.Image,
        time: point.Time,
      });
    });

    (risk?.records || []).forEach((r) => {
      const key = this._coordKey(r.lat, r.lng);
      const loc = index.get(key) || { lat: r.lat, lng: r.lng, name: "Monitoring point" };
      loc.hri = r.heatRiskIndex;
      loc.riskLevel = r.riskLevel;
      index.set(key, loc);
    });

    (climate?.records || []).forEach((r) => {
      const key = this._coordKey(r.lat, r.lng);
      const loc = index.get(key) || { lat: r.lat, lng: r.lng, name: r.locationName };
      loc.climateScore = r.climateResilienceScore;
      loc.climateCategory = r.category;
      loc.name = loc.name || r.locationName;
      if (r.metrics) {
        loc.hri = loc.hri ?? r.metrics.heatRiskIndex;
        loc.riskLevel = loc.riskLevel ?? r.metrics.heatRiskLevel;
        loc.ndvi = loc.ndvi ?? r.metrics.ndvi;
        loc.lst = loc.lst ?? r.metrics.averageTemperature;
      }
      index.set(key, loc);
    });

    (recommendations?.recommendations || []).forEach((r) => {
      const key = this._coordKey(r.lat, r.lng);
      const loc = index.get(key) || { lat: r.lat, lng: r.lng, name: r.locationName };
      loc.recommendation = {
        interventionLevel: r.interventionLevel,
        priorityArea: r.priorityArea,
        deficitScore: r.vegetationDeficitScore,
        actions: r.suggestedActions,
      };
      loc.name = loc.name || r.locationName;
      index.set(key, loc);
    });

    return Array.from(index.values()).map((loc) => {
      loc.alertLevel = this._classifyAlert(loc.lst);
      return loc;
    });
  }

  _classifyAlert(temp) {
    if (temp == null) return "Normal";
    if (temp > 40) return "Extreme";
    if (temp > 38) return "Severe";
    if (temp > 35) return "Warning";
    return "Normal";
  }

  _buildAllLayers() {
    Object.values(this.layerGroups).forEach((group) => group.clearLayers());

    this.locations.forEach((loc) => {
      Object.keys(MAP_LAYERS).forEach((layerId) => {
        if (layerId === "heat-risk") return;
        const style = this._getMarkerStyle(layerId, loc);
        if (!style) return;

        const marker = L.circleMarker([loc.lat, loc.lng], {
          radius: style.radius,
          fillColor: style.fillColor,
          color: style.strokeColor,
          weight: style.weight,
          opacity: style.opacity,
          fillOpacity: style.fillOpacity,
          className: style.className || "",
        });

        marker.bindPopup(this._buildPopup(loc), {
          className: "env-popup",
          maxWidth: 300,
          minWidth: 260,
        });

        this.layerGroups[layerId].addLayer(marker);
      });
    });
  }

  _getMarkerStyle(layerId, loc) {
    switch (layerId) {
      case "lst":
        return {
          radius: 8,
          fillColor: this._lstColor(loc.lst),
          strokeColor: "#ffffff",
          weight: 1.5,
          opacity: 0.95,
          fillOpacity: 0.78,
        };
      case "ndvi":
        return {
          radius: 8,
          fillColor: this._ndviColor(loc.ndvi),
          strokeColor: "#ffffff",
          weight: 1.5,
          opacity: 0.95,
          fillOpacity: 0.78,
        };
      case "heat-risk":
        return {
          radius: 7 + (loc.hri || 0) * 6,
          fillColor: this._hriColor(loc.hri),
          strokeColor: "#ffffff",
          weight: 1.5,
          opacity: 0.95,
          fillOpacity: 0.75,
        };
      case "climate-score":
        return {
          radius: 7 + ((loc.climateScore || 0) / 100) * 4,
          fillColor: this._climateColor(loc.climateScore),
          strokeColor: "#ffffff",
          weight: 1.5,
          opacity: 0.95,
          fillOpacity: 0.78,
        };
      case "recommendations": {
        if (!loc.recommendation) return null;
        const rec = loc.recommendation;
        return {
          radius: rec.priorityArea ? 10 : 7,
          fillColor: this._interventionColor(rec.interventionLevel),
          strokeColor: rec.priorityArea ? "#fbbf24" : "#ffffff",
          weight: rec.priorityArea ? 2.5 : 1.5,
          opacity: 0.95,
          fillOpacity: 0.8,
          className: rec.priorityArea ? "marker-priority" : "",
        };
      }
      case "alerts": {
        const level = loc.alertLevel;
        const isAlert = level !== "Normal";
        return {
          radius: isAlert ? (level === "Extreme" ? 12 : level === "Severe" ? 10 : 9) : 5,
          fillColor: this._alertColor(level),
          strokeColor: "#ffffff",
          weight: isAlert ? 2 : 1,
          opacity: isAlert ? 1 : 0.35,
          fillOpacity: isAlert ? 0.85 : 0.2,
          className: isAlert ? "marker-alert-pulse" : "",
        };
      }
      default:
        return null;
    }
  }

  _lstColor(temp) {
    if (temp >= 35) return this.colors.extreme;
    if (temp >= 32) return this.colors.high;
    if (temp >= 30) return this.colors.moderate;
    return this.colors.vegetation;
  }

  _ndviColor(ndvi) {
    const n = Math.max(0, Math.min(1, ndvi ?? 0));
    if (n >= 0.6) return this.colors.vegetation;
    if (n >= 0.3) return this.colors.moderate;
    if (n >= 0.1) return this.colors.high;
    return this.colors.extreme;
  }

  _hriColor(hri) {
    const h = hri ?? 0;
    if (h >= 0.8) return this.colors.extreme;
    if (h >= 0.6) return this.colors.high;
    if (h >= 0.4) return this.colors.moderate;
    return this.colors.vegetation;
  }

  _climateColor(score) {
    const s = score ?? 0;
    if (s >= 81) return this.colors.cool || "#38bdf8";
    if (s >= 61) return this.colors.vegetation;
    if (s >= 41) return this.colors.moderate;
    if (s >= 21) return this.colors.high;
    return this.colors.extreme;
  }

  _interventionColor(level) {
    if (!level) return this.colors.moderate;
    if (level.includes("Aggressive")) return this.colors.extreme;
    if (level.includes("Moderate")) return this.colors.high;
    return this.colors.vegetation;
  }

  _alertColor(level) {
    const map = {
      Extreme: this.colors.extreme,
      Severe: this.colors.high,
      Warning: this.colors.moderate,
      Normal: this.colors.vegetation,
    };
    return map[level] || this.colors.vegetation;
  }

  _buildPopup(loc) {
    const lstColor = this._lstColor(loc.lst);
    const alertColor = this._alertColor(loc.alertLevel);
    const imageTag = loc.image
      ? `<div class="env-popup__image"><img src="images/${this._escape(loc.image)}" alt="${this._escape(loc.name)}" loading="lazy" onerror="this.closest('.env-popup__image').innerHTML='<span class=\\'env-popup__image-fallback\\'>Ground photo unavailable</span>'" /></div>`
      : "";

    const recBlock = loc.recommendation
      ? `<div class="env-popup__section">
          <div class="env-popup__section-title">Green infrastructure</div>
          <div class="env-popup__badge env-popup__badge--rec">${this._escape(loc.recommendation.interventionLevel)}</div>
          ${loc.recommendation.priorityArea ? '<span class="env-popup__tag">Priority area</span>' : ""}
          <ul class="env-popup__actions">${(loc.recommendation.actions || [])
              .map((a) => `<li>${this._escape(a)}</li>`)
              .join("")}</ul>
        </div>`
      : "";

    return `
      <div class="env-popup__card">
        <div class="env-popup__header" style="--accent:${lstColor}">
          <div>
            <h3 class="env-popup__title">${this._escape(loc.name || "Monitoring point")}</h3>
            <p class="env-popup__coords">${loc.lat?.toFixed(5)}, ${loc.lng?.toFixed(5)}</p>
          </div>
          <span class="env-popup__alert-pill" style="background:${alertColor}22;color:${alertColor};border-color:${alertColor}55">
            ${loc.alertLevel}
          </span>
        </div>
        ${imageTag}
        <div class="env-popup__metrics">
          <div class="env-popup__metric">
            <span class="env-popup__metric-label">LST</span>
            <span class="env-popup__metric-value" style="color:${lstColor}">${loc.lst ?? "—"}°C</span>
          </div>
          <div class="env-popup__metric">
            <span class="env-popup__metric-label">NDVI</span>
            <span class="env-popup__metric-value">${loc.ndvi ?? "—"}</span>
          </div>
          <div class="env-popup__metric">
            <span class="env-popup__metric-label">Heat Risk</span>
            <span class="env-popup__metric-value">${loc.hri != null ? (loc.hri * 100).toFixed(1) + "%" : "—"}</span>
          </div>
          <div class="env-popup__metric">
            <span class="env-popup__metric-label">Resilience</span>
            <span class="env-popup__metric-value">${loc.climateScore != null ? Math.round(loc.climateScore) + "/100" : "—"}</span>
          </div>
        </div>
        <div class="env-popup__details">
          <span><strong>Surface</strong> ${this._escape(loc.surface || "—")}</span>
          <span><strong>Traffic</strong> ${this._escape(loc.traffic || "—")}</span>
          <span><strong>Risk level</strong> ${this._escape(loc.riskLevel || "—")}</span>
          <span><strong>Category</strong> ${this._escape(loc.climateCategory || "—")}</span>
        </div>
        ${recBlock}
      </div>
    `;
  }

  _escape(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  _shouldShowRegionGeojson(layerId) {
    return ["lst", "ndvi", "heat-risk"].includes(layerId);
  }

  _renderGeojson(coords) {
    if (this.geojsonLayer) {
      this.map.removeLayer(this.geojsonLayer);
      this.geojsonLayer = null;
    }
    if (!coords?.geojson) return;

    this.geojsonLayer = L.geoJSON(coords.geojson, {
      style: (feature) => {
        const intensity = feature.properties.intensity;
        const fillColor =
          intensity > 0.7
            ? this.colors.extreme
            : intensity > 0.5
              ? this.colors.high
              : intensity > 0.3
                ? this.colors.moderate
                : this.colors.vegetation;
        return {
          color: fillColor,
          weight: 1,
          opacity: 0.3,
          fillColor,
          fillOpacity: 0.1,
        };
      },
      onEachFeature: (feature, layer) => {
        const props = feature.properties || {};
        layer.bindPopup(
          `<div class="env-popup__card"><h3 class="env-popup__title">${this._escape(props.name || "Region zone")}</h3>
          <p>Avg LST: ${props.avg_lst ?? "—"}°C · Intensity: ${props.intensity ?? "—"}</p></div>`,
          { className: "env-popup", maxWidth: 280 }
        );
      },
    });

    if (this._shouldShowRegionGeojson(this.activeLayer)) {
      this.geojsonLayer.addTo(this.map);
    }
  }

  setUserGeoJSON(geojsonDocument, options = {}) {
    this.clearUserGeoJSON();

    this.userGeojsonLayer = L.geoJSON(geojsonDocument, {
      style: {
        color: options.strokeColor || "#38bdf8",
        weight: 2,
        opacity: 0.85,
        fillColor: options.fillColor || "#38bdf8",
        fillOpacity: 0.12,
        dashArray: "6 4",
      },
      onEachFeature: (feature, layer) => {
        const props = feature.properties || {};
        const name = props.name || props.Name || "Uploaded polygon";
        layer.bindPopup(
          `<div class="env-popup__card"><h3 class="env-popup__title">${this._escape(name)}</h3>
          <p class="env-popup__coords">User GeoJSON feature</p></div>`,
          { className: "env-popup", maxWidth: 260 }
        );
      },
    }).addTo(this.map);

    try {
      const bounds = this.userGeojsonLayer.getBounds();
      if (bounds.isValid()) {
        this.map.fitBounds(bounds, { padding: [40, 40], maxZoom: 16 });
      }
    } catch {
      /* ignore invalid bounds */
    }
  }

  clearUserGeoJSON() {
    if (this.userGeojsonLayer) {
      this.map.removeLayer(this.userGeojsonLayer);
      this.userGeojsonLayer = null;
    }
  }

  _syncUserGeojsonVisibility() {
    if (!this.userGeojsonLayer) return;
    if (!this.map.hasLayer(this.userGeojsonLayer)) {
      this.userGeojsonLayer.addTo(this.map);
    }
  }

  switchLayer(layerId) {
    if (!MAP_LAYERS[layerId] || !this.enabledLayers.includes(layerId)) return;
    if (this.isTransitioning || layerId === this.activeLayer) return;

    const oldLayer = this.activeLayer;
    const wrapper = document.getElementById(this.wrapperId);

    this.isTransitioning = true;
    if (wrapper) wrapper.classList.add("map-layer-transitioning");

    const markerPane = this.map.getPane("markerPane");
    const panes = [markerPane, this.map.getPane("overlayPane")].filter(Boolean);
    panes.forEach((pane) => {
      pane.style.transition = "opacity 0.32s ease";
      pane.style.opacity = "0";
    });

    setTimeout(() => {
      if (oldLayer === "heat-risk") {
        this.heatRiskViz?.hide();
      } else if (this.layerGroups[oldLayer]?.getLayers().length) {
        this.map.removeLayer(this.layerGroups[oldLayer]);
      }

      this.activeLayer = layerId;

      if (layerId === "heat-risk" && this.heatRiskViz) {
        this.heatRiskViz.show();
      } else {
        this.layerGroups[layerId].addTo(this.map);
      }

      if (this.geojsonLayer) {
        if (this._shouldShowRegionGeojson(layerId)) {
          if (!this.map.hasLayer(this.geojsonLayer)) this.geojsonLayer.addTo(this.map);
        } else if (this.map.hasLayer(this.geojsonLayer)) {
          this.map.removeLayer(this.geojsonLayer);
        }
      }
      this._syncUserGeojsonVisibility();

      this._updateLegend(layerId);
      this._updateLayerPanel(layerId);
      this.heatRiskViz?.closeDetail();

      requestAnimationFrame(() => {
        panes.forEach((pane) => {
          pane.style.opacity = "1";
        });
        setTimeout(() => {
          panes.forEach((pane) => {
            pane.style.transition = "";
          });
          if (wrapper) wrapper.classList.remove("map-layer-transitioning");
          this.isTransitioning = false;
        }, 340);
      });
    }, 320);
  }

  _updateLayerPanel(layerId) {
    if (!this.layerPanelEl) return;
    this.layerPanelEl.querySelectorAll(".map-layer-option").forEach((btn) => {
      const isActive = btn.dataset.layer === layerId;
      btn.classList.toggle("is-active", isActive);
      btn.setAttribute("aria-checked", isActive ? "true" : "false");
    });
  }

  _updateLegend(layerId) {
    let legendEl = document.getElementById("map-legend");
    if (!legendEl) {
      const wrapper = document.getElementById(this.wrapperId);
      legendEl = document.createElement("div");
      legendEl.id = "map-legend";
      legendEl.className = "map-legend";
      legendEl.setAttribute("role", "img");
      wrapper?.appendChild(legendEl);
    }

    if (layerId === "heat-risk" && this.heatRiskViz) {
      this.heatRiskViz.renderGradientLegend(legendEl);
      return;
    }

    const layer = MAP_LAYERS[layerId];
    const items = (LAYER_LEGENDS[layerId] || [])
      .map(
        (item) => `
        <div class="legend-item">
          <div class="legend-color ${item.class}"></div>
          <span>${item.label}</span>
        </div>`
      )
      .join("");

    legendEl.innerHTML = `
      <div class="legend-title">${layer?.label || "Layer"} scale</div>
      ${items}
    `;
  }

  invalidateSize() {
    this.map?.invalidateSize();
    this._syncMinimap();
  }
}

window.MapEngine = MapEngine;
window.MAP_LAYERS = MAP_LAYERS;
