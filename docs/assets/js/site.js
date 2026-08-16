// depotdiary — gemeinsame Website-Logik. Kein Framework, kein Build-Schritt.

const CATEGORY_LABELS = {
  "depot-update": "Depot-Update",
  "wochennotiz": "Wochennotiz",
  "erklaerstueck": "Erklärstück",
  "quartalszahlen": "Quartalszahlen",
  "fehler": "Fehler",
};

async function fetchJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Konnte ${path} nicht laden (${res.status})`);
  return res.json();
}

// *wort* -> <em class="accent">wort</em>, wie im Slide-System (render.py)
function renderAccent(text) {
  const escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return escaped.replace(/\*([^*]+)\*/g, '<em class="accent">$1</em>');
}

function formatDate(iso) {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("de-AT", { year: "numeric", month: "long", day: "numeric" });
}

function categoryLabel(cat) {
  return CATEGORY_LABELS[cat] || cat;
}

function postCardHTML(post) {
  const href = post.url || post.cover || "#";
  return `
    <a class="post-card" href="${href}" target="${post.url ? "_blank" : "_self"}" rel="noopener">
      <img src="${post.cover}" alt="" loading="lazy">
      <div class="post-card-body">
        <p class="eyebrow">${categoryLabel(post.category)}</p>
        <h3>${renderAccent(post.title)}</h3>
        <span class="post-date">${formatDate(post.date)}</span>
        <p class="excerpt">${renderAccent(post.excerpt || "")}</p>
      </div>
    </a>`;
}

// --- Startseite ---
async function initHome() {
  try {
    const depot = await fetchJSON("content/depot.json");
    const allocEl = document.getElementById("allocation");
    const lastUpdatedEl = document.getElementById("last-updated");
    if (lastUpdatedEl && depot.updated) {
      lastUpdatedEl.hidden = false;
      lastUpdatedEl.textContent = `Zuletzt aktualisiert: ${formatDate(depot.updated)}`;
    }
    if (allocEl && depot.categories) {
      const placeholderNote = depot.placeholder
        ? `<p class="result-count" style="color:var(--red);margin-bottom:14px;">Platzhalter-Daten — noch keine echte Depot-Allokation hinterlegt.</p>`
        : "";
      allocEl.innerHTML = placeholderNote + depot.categories.map(c => `
        <div class="allocation-row">
          <div class="allocation-label">
            <span>${c.label}</span>
            <span class="allocation-value">${c.percent}%</span>
          </div>
          <div class="allocation-track">
            <div class="allocation-fill" style="width:${c.percent}%"></div>
          </div>
        </div>`).join("") +
        `<p class="allocation-updated">Stand: ${formatDate(depot.updated)}${depot.change_note ? " — " + renderAccent(depot.change_note) : ""}</p>`;
    }
  } catch (e) {
    const allocEl = document.getElementById("allocation");
    if (allocEl) allocEl.innerHTML = `<p class="empty-state">Noch keine Depotdaten hinterlegt.</p>`;
  }

  try {
    const posts = await fetchJSON("content/posts.json");
    const latest = [...posts].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 4);
    const grid = document.getElementById("latest-posts");
    if (grid) {
      grid.innerHTML = latest.length
        ? latest.map(postCardHTML).join("")
        : `<p class="empty-state">Noch keine Posts hinterlegt.</p>`;
    }
  } catch (e) {
    console.error(e);
  }
}

// --- Archiv ---
const MONTH_NAMES = ["Januar", "Februar", "März", "April", "Mai", "Juni",
  "Juli", "August", "September", "Oktober", "November", "Dezember"];

async function initArchiv() {
  const posts = await fetchJSON("content/posts.json");
  const grid = document.getElementById("archiv-grid");
  const searchInput = document.getElementById("archiv-search");
  const categorySelect = document.getElementById("archiv-category");
  const yearSelect = document.getElementById("archiv-year");
  const monthSelect = document.getElementById("archiv-month");
  const countEl = document.getElementById("archiv-count");

  const uniqueCategories = [...new Set(posts.map(p => p.category))];
  categorySelect.innerHTML = `<option value="">Alle Kategorien</option>` +
    uniqueCategories.map(c => `<option value="${c}">${categoryLabel(c)}</option>`).join("");

  const uniqueYears = [...new Set(posts.map(p => p.date.slice(0, 4)))].sort((a, b) => b.localeCompare(a));
  yearSelect.innerHTML = `<option value="">Alle Jahre</option>` +
    uniqueYears.map(y => `<option value="${y}">${y}</option>`).join("");

  const uniqueMonths = [...new Set(posts.map(p => p.date.slice(5, 7)))].sort();
  monthSelect.innerHTML = `<option value="">Alle Monate</option>` +
    uniqueMonths.map(m => `<option value="${m}">${MONTH_NAMES[parseInt(m, 10) - 1]}</option>`).join("");

  function render() {
    const q = searchInput.value.trim().toLowerCase();
    const cat = categorySelect.value;
    const year = yearSelect.value;
    const month = monthSelect.value;
    const filtered = posts
      .filter(p => !cat || p.category === cat)
      .filter(p => !year || p.date.slice(0, 4) === year)
      .filter(p => !month || p.date.slice(5, 7) === month)
      .filter(p => !q || (p.title + " " + (p.excerpt || "")).toLowerCase().includes(q))
      .sort((a, b) => b.date.localeCompare(a.date));

    grid.innerHTML = filtered.length
      ? filtered.map(postCardHTML).join("")
      : `<p class="empty-state">Keine Posts gefunden.</p>`;
    countEl.textContent = `${filtered.length} von ${posts.length} Posts`;
  }

  searchInput.addEventListener("input", render);
  categorySelect.addEventListener("change", render);
  yearSelect.addEventListener("change", render);
  monthSelect.addEventListener("change", render);
  render();
}

// --- Wissen ---
async function initWissen() {
  const entries = await fetchJSON("content/wissen.json");
  const sorted = [...entries].sort((a, b) => b.date.localeCompare(a.date));

  const nav = document.getElementById("wissen-nav");
  const list = document.getElementById("wissen-list");

  if (!sorted.length) {
    list.innerHTML = `<p class="empty-state">Noch keine Erklärstücke hinterlegt.</p>`;
    return;
  }

  nav.innerHTML = sorted.map(e => `<a href="#${e.id}">${renderAccent(e.title)}</a>`).join("");
  list.innerHTML = sorted.map(e => `
    <article class="wissen-entry" id="${e.id}">
      <span class="post-date">${formatDate(e.date)}</span>
      <h2>${renderAccent(e.title)}</h2>
      ${(e.body || []).map(p => `<p>${renderAccent(p)}</p>`).join("")}
    </article>`).join("");
}

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;
  const handlers = { home: initHome, archiv: initArchiv, wissen: initWissen };
  if (handlers[page]) handlers[page]().catch(err => console.error(err));
});
