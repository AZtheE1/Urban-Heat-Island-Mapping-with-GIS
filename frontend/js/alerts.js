/**
 * Climate Alert Center — Real-time heatwave monitoring
 */

const REGIONS = [
  { id: "dhaka_all", name: "Dhaka" },
  { id: "mirpur12", name: "Mirpur 12" },
  { id: "sylhet", name: "Sylhet" },
  { id: "rajshahi", name: "Rajshahi" },
  { id: "chittagong", name: "Chittagong" },
];

const LEVEL_RANK = { Normal: 0, Warning: 1, Severe: 2, Extreme: 3 };
const REFRESH_MS = 45000;

let state = {
  activeAlerts: [],
  historyAlerts: [],
  notifications: [],
  regionFilter: "all",
  lastSync: null,
  seenIds: new Set(),
};

let refreshTimer = null;

document.addEventListener("DOMContentLoaded", () => {
  bindEvents();
  loadAlerts();
  refreshTimer = setInterval(loadAlerts, REFRESH_MS);
});

function bindEvents() {
  document.getElementById("btn-refresh").addEventListener("click", () => loadAlerts(true));
  document.getElementById("filter-region").addEventListener("change", (e) => {
    state.regionFilter = e.target.value;
    renderAll();
  });
}

async function loadAlerts(manual = false) {
  const btn = document.getElementById("btn-refresh");
  if (manual) btn.classList.add("is-spinning");
  setLoading(true);

  try {
    const regionIds =
      state.regionFilter === "all"
        ? REGIONS.map((r) => r.id)
        : [state.regionFilter];

    const results = await Promise.all(
      regionIds.map((id) =>
        fetch(`/api/alerts?region=${id}&includeHistorical=true`).then(async (res) => {
          if (!res.ok) return null;
          const data = await res.json();
          return { ...data, regionId: id };
        })
      )
    );

    const valid = results.filter(Boolean);
    mergeAlertData(valid);
    pushNewNotifications();
    renderAll();

    state.lastSync = new Date();
    document.getElementById("last-sync").textContent = formatTime(state.lastSync);
  } catch (err) {
    console.error("Alert sync failed:", err);
  } finally {
    setLoading(false);
    btn.classList.remove("is-spinning");
  }
}

function mergeAlertData(regionResults) {
  const active = [];
  const history = [];

  regionResults.forEach((result) => {
    const regionName = result.name || result.region;
    (result.alerts || []).forEach((alert) => {
      const enriched = {
        ...alert,
        region: alert.region || result.region,
        regionName,
      };
      if (enriched.source === "historical_temperature_log") {
        history.push(enriched);
      } else {
        active.push(enriched);
      }
    });
  });

  active.sort(
    (a, b) =>
      LEVEL_RANK[b.level] - LEVEL_RANK[a.level] ||
      b.temperature - a.temperature
  );
  history.sort(
    (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
  );

  state.activeAlerts = active;
  state.historyAlerts = history;
}

function pushNewNotifications() {
  const newItems = state.activeAlerts.filter((a) => {
    const id = alertId(a);
    if (state.seenIds.has(id)) return false;
    state.seenIds.add(id);
    return true;
  });

  if (newItems.length === 0) return;

  const notifs = newItems.map((a) => ({
    ...a,
    isNew: true,
    receivedAt: new Date().toISOString(),
  }));

  state.notifications = [...notifs, ...state.notifications].slice(0, 30);
}

function alertId(alert) {
  return alert.id || `${alert.region}-${alert.locationName}-${alert.temperature}-${alert.timestamp}`;
}

function renderAll() {
  const filtered = filterByRegion(state.activeAlerts);
  const filteredHistory = filterByRegion(state.historyAlerts);
  const filteredNotifs = filterByRegion(state.notifications);

  renderKpis(filtered, filteredHistory);
  renderNotifications(filteredNotifs);
  renderActiveAlerts(filtered);
  renderTimeline([...filtered, ...filteredHistory].slice(0, 20));
  renderHistory(filteredHistory);
  updateLiveIndicator(filtered);
}

function filterByRegion(alerts) {
  if (state.regionFilter === "all") return alerts;
  return alerts.filter((a) => a.region === state.regionFilter);
}

function renderKpis(active, history) {
  document.getElementById("kpi-active").textContent = active.length;

  const highest = active.length
    ? active.reduce((best, a) =>
        LEVEL_RANK[a.level] > LEVEL_RANK[best.level] ? a : best
      )
    : null;

  const severityEl = document.getElementById("kpi-severity");
  if (highest) {
    severityEl.textContent = highest.level;
    severityEl.className = `alert-kpi__value is-${highest.level.toLowerCase()}`;
  } else {
    severityEl.textContent = "Normal";
    severityEl.className = "alert-kpi__value is-normal";
  }

  const regionsOnWatch = new Set(active.map((a) => a.region)).size;
  document.getElementById("kpi-regions").textContent =
    regionsOnWatch > 0 ? `${regionsOnWatch} / ${REGIONS.length}` : "0";

  document.getElementById("kpi-history").textContent = history.length;
  document.getElementById("notif-count").textContent = filterByRegion(state.notifications).length;

  const subtitle = document.getElementById("active-subtitle");
  subtitle.textContent =
    active.length > 0
      ? `${active.length} threshold breach${active.length !== 1 ? "es" : ""} detected`
      : "Real-time threshold breaches";
}

function renderNotifications(notifications) {
  const feed = document.getElementById("notification-feed");
  if (!notifications.length) {
    feed.innerHTML = `<p class="alert-empty">No notifications in queue.</p>`;
    return;
  }

  feed.innerHTML = notifications
    .slice(0, 15)
    .map(
      (n) => `
      <article class="notification-item notification-item--${n.level}${n.isNew ? " is-new" : ""}">
        <span class="notification-item__indicator" aria-hidden="true"></span>
        <div>
          <span class="notification-item__level">${escapeHtml(n.level)}</span>
          <p class="notification-item__msg">${escapeHtml(n.message)}</p>
          <p class="notification-item__meta">${escapeHtml(n.regionName || n.region)} · ${formatTimestamp(n.timestamp)}</p>
        </div>
      </article>`
    )
    .join("");

  notifications.forEach((n) => { n.isNew = false; });
}

function renderActiveAlerts(alerts) {
  const grid = document.getElementById("active-alerts-grid");

  if (!alerts.length) {
    grid.innerHTML = `
      <div class="alert-empty-state" id="active-empty">
        <div class="alert-empty-state__icon" aria-hidden="true">
          <span class="severity-dot severity-dot--normal"></span>
        </div>
        <h3>No active heatwave alerts</h3>
        <p>All monitored jurisdictions are within normal temperature thresholds.</p>
      </div>`;
    return;
  }

  grid.innerHTML = alerts
    .map(
      (a) => `
    <article class="active-alert-card active-alert-card--${a.level}">
      <span class="active-alert-card__pulse" aria-hidden="true"></span>
      <div class="active-alert-card__header">
        <span class="active-alert-card__level">${escapeHtml(a.level)}</span>
        <span class="active-alert-card__temp">${a.temperature}°C</span>
      </div>
      <p class="active-alert-card__location">${escapeHtml(a.locationName || "Monitoring station")}</p>
      <p class="active-alert-card__region">${escapeHtml(a.regionName || a.region)}</p>
      <p class="active-alert-card__message">${escapeHtml(a.message)}</p>
    </article>`
    )
    .join("");
}

function renderTimeline(events) {
  const timeline = document.getElementById("alert-timeline");
  const sorted = [...events].sort(
    (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
  );

  if (!sorted.length) {
    timeline.innerHTML = `<p class="alert-empty">No timeline events yet.</p>`;
    return;
  }

  timeline.innerHTML = sorted
    .map(
      (e, i) => `
    <div class="timeline-event timeline-event--${e.level}" style="animation-delay:${i * 0.04}s">
      <span class="timeline-event__dot" aria-hidden="true"></span>
      <p class="timeline-event__time">${formatTimestamp(e.timestamp)}</p>
      <p class="timeline-event__title">${escapeHtml(e.level)} · ${e.temperature}°C</p>
      <p class="timeline-event__detail">${escapeHtml(e.locationName || e.regionName || e.region)}${e.source === "historical_temperature_log" ? " · Historical" : ""}</p>
    </div>`
    )
    .join("");
}

function renderHistory(history) {
  const tbody = document.getElementById("history-body");

  if (!history.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="alert-empty">No historical heatwave events recorded.</td></tr>`;
    return;
  }

  tbody.innerHTML = history
    .slice(0, 50)
    .map(
      (h) => `
    <tr>
      <td>
        <span class="history-severity history-severity--${h.level}">
          <span class="history-severity__dot"></span>
          ${escapeHtml(h.level)}
        </span>
      </td>
      <td><span class="history-temp">${h.temperature}°C</span></td>
      <td>${escapeHtml(h.locationName || "—")}</td>
      <td>${escapeHtml(h.regionName || h.region)}</td>
      <td>${formatTimestamp(h.timestamp)}</td>
      <td>${escapeHtml(h.message)}</td>
    </tr>`
    )
    .join("");
}

function updateLiveIndicator(active) {
  const indicator = document.getElementById("live-indicator");
  const hasCritical = active.some((a) => a.level === "Extreme" || a.level === "Severe");
  indicator.classList.toggle("is-alerting", hasCritical);
}

function setLoading(on) {
  document.body.classList.toggle("is-loading", on);
}

function formatTimestamp(ts) {
  if (!ts) return "—";
  try {
    return new Date(ts).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return ts;
  }
}

function formatTime(date) {
  return date.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

window.addEventListener("beforeunload", () => {
  if (refreshTimer) clearInterval(refreshTimer);
});
