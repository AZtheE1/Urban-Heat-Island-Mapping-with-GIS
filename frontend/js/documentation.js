/**
 * Research Overview — Documentation renderer
 * Content loaded from /api/project-documentation (JSON data source)
 */

const TOC_SECTIONS = [
  { id: "section-overview", label: "Overview" },
  { id: "section-problem", label: "Problem Statement" },
  { id: "section-objectives", label: "Objectives" },
  { id: "section-uhi", label: "UHI Explained" },
  { id: "section-team", label: "Team Gliders" },
  { id: "section-methodology", label: "Methodology" },
  { id: "section-architecture", label: "Architecture" },
  { id: "section-technologies", label: "Technologies" },
  { id: "section-findings", label: "Findings" },
  { id: "section-features", label: "Features" },
  { id: "section-future", label: "Future Work" },
  { id: "section-references", label: "References" },
];

document.addEventListener("DOMContentLoaded", () => {
  initToc();
  loadDocumentation();
});

function setLoading(on) {
  document.body.classList.toggle("is-loading", on);
}

async function loadDocumentation() {
  setLoading(true);
  try {
    const res = await fetch("/api/project-documentation");
    if (!res.ok) throw new Error("Failed to load project documentation.");
    const data = await res.json();
    renderAll(data);
  } catch (err) {
    console.error(err);
    document.getElementById("docs-main").innerHTML =
      `<p class="docs-section__lead" style="color:var(--heat-extreme)">${escapeHtml(err.message)}</p>`;
  } finally {
    setLoading(false);
  }
}

function renderAll(data) {
  const { meta, overview, team, methodology, architecture, technologies, findings, features, futureWork, references } = data;

  document.getElementById("docs-header-subtitle").textContent =
    `${meta.institution} · ${meta.course}`;

  document.getElementById("docs-meta-badge").textContent =
    `${meta.group} · ${meta.department}`;

  document.getElementById("overview-heading").textContent = overview.thesisTitle;
  document.getElementById("docs-thesis-subtitle").textContent = overview.thesisSubtitle;

  document.getElementById("docs-hero-meta").innerHTML = [
    overview.degree,
    overview.submissionDate,
    meta.institution,
  ]
    .map((t) => `<span>${escapeHtml(t)}</span>`)
    .join("");

  document.getElementById("docs-problem").textContent = overview.problemStatement;

  document.getElementById("docs-objectives").innerHTML = overview.objectives
    .map((obj) => `<li>${escapeHtml(obj)}</li>`)
    .join("");

  document.getElementById("docs-significance").textContent = overview.significance;

  renderUhi(overview.uhiExplanation);
  renderTeam(team);
  renderMethodology(methodology);
  renderArchitecture(architecture);
  renderTechnologies(technologies);
  renderFindings(findings);
  renderFeatures(features);
  renderFuture(futureWork);
  renderReferences(references);

  document.getElementById("docs-footer").innerHTML =
    `© ${new Date().getFullYear()} ${escapeHtml(team.name)} · ${escapeHtml(meta.group)} · ` +
    `Documentation v${escapeHtml(meta.version)} · Last updated ${escapeHtml(meta.lastUpdated)}`;
}

function renderUhi(uhi) {
  document.getElementById("uhi-heading").textContent = uhi.title;
  document.getElementById("docs-uhi").innerHTML = `
    <div class="docs-uhi-card docs-uhi-card--full">
      <h4>Definition</h4>
      <p>${escapeHtml(uhi.summary)}</p>
    </div>
    <div class="docs-uhi-card">
      <h4>Primary Causes</h4>
      <ul>${uhi.causes.map((c) => `<li>${escapeHtml(c)}</li>`).join("")}</ul>
    </div>
    <div class="docs-uhi-card">
      <h4>Environmental Impacts</h4>
      <ul>${uhi.impacts.map((i) => `<li>${escapeHtml(i)}</li>`).join("")}</ul>
    </div>
  `;
}

function renderTeam(team) {
  document.getElementById("team-heading").textContent = team.name;
  document.getElementById("docs-team-tagline").textContent = team.tagline;

  document.getElementById("docs-team").innerHTML = team.pairs
    .map((pair) => {
      const members = pair.members
        .map((m) => {
          const initials = m.name
            .split(" ")
            .map((w) => w[0])
            .join("")
            .slice(0, 2)
            .toUpperCase();
          return `
            <div class="docs-member-card">
              <div class="docs-member-card__avatar" style="background:${pair.color}22;color:${pair.color};border:1px solid ${pair.color}55">${initials}</div>
              <div class="docs-member-card__info">
                <div class="docs-member-card__name">${escapeHtml(m.name)}</div>
                <div class="docs-member-card__meta">ID ${escapeHtml(m.studentId)} · ${escapeHtml(m.role)}</div>
              </div>
            </div>`;
        })
        .join("");

      const resp = pair.responsibilities
        .map((r) => `<li>${escapeHtml(r)}</li>`)
        .join("");

      return `
        <article class="docs-pair-card" style="--pair-color:${pair.color}">
          <div class="docs-pair-card__head" style="background:${pair.color}12;border-bottom-color:${pair.color}33">
            <div class="docs-pair-card__label" style="color:${pair.color}">${escapeHtml(pair.label)}</div>
            <div class="docs-pair-card__title">${escapeHtml(pair.title)}</div>
          </div>
          <div class="docs-pair-card__resp">
            <ul>${resp}</ul>
          </div>
          <div class="docs-pair-card__members">${members}</div>
        </article>`;
    })
    .join("");
}

function renderMethodology(methodology) {
  document.getElementById("methodology-heading").textContent = methodology.title;
  document.getElementById("docs-methodology-subtitle").textContent = methodology.subtitle;

  document.getElementById("docs-timeline").innerHTML = methodology.steps
    .map(
      (step) => `
      <article class="docs-timeline__item" data-step="${step.step}">
        <h4 class="docs-timeline__title">Step ${step.step}: ${escapeHtml(step.title)}</h4>
        <p class="docs-timeline__desc">${escapeHtml(step.description)}</p>
      </article>`
    )
    .join("");
}

function renderArchitecture(architecture) {
  document.getElementById("architecture-heading").textContent = architecture.title;
  document.getElementById("docs-architecture-subtitle").textContent = architecture.subtitle;

  const layers = architecture.layers
    .map((layer, i) => {
      const arrow =
        i < architecture.layers.length - 1
          ? `<div class="docs-arch-arrow" aria-hidden="true">↓</div>`
          : "";
      return `
        <div class="docs-arch-layer">
          <div class="docs-arch-layer__icon">${layer.icon}</div>
          <div class="docs-arch-layer__title">${escapeHtml(layer.title)}</div>
          <div class="docs-arch-layer__desc">${escapeHtml(layer.description)}</div>
        </div>
        ${arrow}`;
    })
    .join("");

  document.getElementById("docs-architecture").innerHTML = layers;
}

function renderTechnologies(technologies) {
  document.getElementById("docs-technologies").innerHTML = technologies
    .map(
      (tech) => `
      <div class="docs-tech-card">
        <div class="docs-tech-card__icon">${tech.icon}</div>
        <div class="docs-tech-card__name">${escapeHtml(tech.name)}</div>
        <div class="docs-tech-card__cat">${escapeHtml(tech.category)}</div>
        <div class="docs-tech-card__desc">${escapeHtml(tech.description)}</div>
      </div>`
    )
    .join("");
}

function renderFindings(findings) {
  document.getElementById("docs-findings").innerHTML = findings
    .map(
      (f) => `
      <article class="docs-finding-card docs-finding-card--${f.type}">
        <div class="docs-finding-card__metric">${escapeHtml(f.metric)}</div>
        <h4 class="docs-finding-card__title">${escapeHtml(f.title)}</h4>
        <p class="docs-finding-card__detail">${escapeHtml(f.detail)}</p>
      </article>`
    )
    .join("");
}

function renderFeatures(features) {
  document.getElementById("docs-features").innerHTML = features
    .map((f) => {
      const tag = f.route
        ? `<a href="${escapeHtml(f.route)}" class="docs-feature-card">`
        : `<div class="docs-feature-card">`;
      const close = f.route ? `</a>` : `</div>`;
      const linkHint = f.route
        ? `<span class="docs-feature-card__link">Open module →</span>`
        : "";
      return `
        ${tag}
          <div class="docs-feature-card__icon">${f.icon}</div>
          <div class="docs-feature-card__name">${escapeHtml(f.name)}</div>
          <div class="docs-feature-card__desc">${escapeHtml(f.description)}</div>
          ${linkHint}
        ${close}`;
    })
    .join("");
}

function renderFuture(items) {
  document.getElementById("docs-future").innerHTML = items
    .map(
      (item, i) => `
      <article class="docs-future-item">
        <span class="docs-future-item__num">${String(i + 1).padStart(2, "0")}</span>
        <div>
          <h4 class="docs-future-item__title">${escapeHtml(item.title)}</h4>
          <p class="docs-future-item__desc">${escapeHtml(item.description)}</p>
        </div>
      </article>`
    )
    .join("");
}

function renderReferences(references) {
  document.getElementById("docs-references").innerHTML = references
    .map(
      (ref) => `
      <li>
        <p class="docs-ref-citation">${escapeHtml(ref.citation)}</p>
        <span class="docs-ref-topic">${escapeHtml(ref.topic)}</span>
      </li>`
    )
    .join("");
}

function initToc() {
  const toc = document.getElementById("docs-toc");
  toc.innerHTML = TOC_SECTIONS.map(
    (s) => `<a href="#${s.id}" class="docs-toc__link" data-section="${s.id}">${escapeHtml(s.label)}</a>`
  ).join("");

  toc.querySelectorAll(".docs-toc__link").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      document.getElementById(link.dataset.section)?.scrollIntoView({ behavior: "smooth" });
    });
  });

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          toc.querySelectorAll(".docs-toc__link").forEach((l) => {
            l.classList.toggle("is-active", l.dataset.section === entry.target.id);
          });
        }
      });
    },
    { rootMargin: "-20% 0px -60% 0px", threshold: 0 }
  );

  TOC_SECTIONS.forEach((s) => {
    const el = document.getElementById(s.id);
    if (el) observer.observe(el);
  });
}

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
