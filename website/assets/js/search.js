const DOCS_INDEX = [
  { title: "compute_gini()", path: "/docs/core#gini", cat: "Core Inequality", desc: "Population-weighted Gini coefficient via Lorenz curve area" },
  { title: "compute_palma_ratio()", path: "/docs/core#palma", cat: "Core Inequality", desc: "Top 10% / Bottom 40% ratio with continuous boundary splits" },
  { title: "compute_concentration_index()", path: "/docs/core#ci", cat: "Core Inequality", desc: "Wagstaff Concentration Index with tied fractional rank handling" },
  { title: "compute_score()", path: "/docs/scoring", cat: "Composite Scoring", desc: "Weighted 0-100 composite score with graceful missing-term dropping" },
  { title: "Catalogue Registry", path: "/docs/catalogue", cat: "Harmonization", desc: "Same / replace / omit questionnaire contracts for cross-country studies" },
  { title: "compute_vulnerability_index()", path: "/docs/frames#vulnerability", cat: "DataFrame Helpers", desc: "Min-max normalized equal-weighted 0-100 vulnerability series" },
  { title: "identify_multiply_deprived()", path: "/docs/frames#multiply-deprived", cat: "DataFrame Helpers", desc: "Flag rows in worst tertiles across multiple deprivation factors" },
  { title: "moveq gini CLI", path: "/docs/cli#gini", cat: "CLI Reference", desc: "Compute population-weighted Gini from CSV" },
  { title: "moveq palma CLI", path: "/docs/cli#palma", cat: "CLI Reference", desc: "Compute Palma ratio from CSV" },
  { title: "moveq ci CLI", path: "/docs/cli#ci", cat: "CLI Reference", desc: "Compute Wagstaff Concentration Index from CSV" },
  { title: "GTFS & r5py Guide", path: "/guides#gtfs", cat: "Guides", desc: "Compute transit equity from raw GTFS feeds using r5py and moveq" },
  { title: "Title VI Environmental Justice", path: "/guides#title-vi", cat: "Guides", desc: "Audit transit equity and generate Federal Title VI reports" },
  { title: "v0.1.2 correctness patch", path: "/blog#v0-1-2", cat: "Blog", desc: "Palma boundary splits, tied-rank CI, zero-service conventions, score validation" },
  { title: "Why discrete Palma binning fails", path: "/blog#palma-boundaries", cat: "Blog", desc: "MAUP at 40/90 population cuts and continuous proportional boundary splitting" },
  { title: "v0.1.1 PyPI documentation", path: "/blog#v0-1-1", cat: "Blog", desc: "Package READMEs explain metrics, not only API call signatures" },
  { title: "Announcing moveq v0.1.0", path: "/blog#v0-1-0", cat: "Blog", desc: "First lockstep release of core, catalogue, umbrella, and CLI" },
  { title: "Static site CI and Vercel deploys", path: "/blog#site", cat: "Blog", desc: "Clean-URL checks and pytest for website/ with no Node build" }
];

window.openSearch = function() {
  const modal = document.getElementById("searchModal");
  if (!modal) return;
  modal.classList.add("open");
  const input = document.getElementById("searchInput");
  if (input) {
    input.value = "";
    input.focus();
    renderSearchResults("");
  }
};

window.closeSearch = function() {
  const modal = document.getElementById("searchModal");
  if (modal) modal.classList.remove("open");
};

function renderSearchResults(query) {
  const resultsContainer = document.getElementById("searchResults");
  if (!resultsContainer) return;

  const q = query.toLowerCase().trim();
  const filtered = q === "" 
    ? DOCS_INDEX.slice(0, 6) 
    : DOCS_INDEX.filter(item => 
        item.title.toLowerCase().includes(q) || 
        item.desc.toLowerCase().includes(q) || 
        item.cat.toLowerCase().includes(q)
      );

  if (filtered.length === 0) {
    resultsContainer.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-faint);">No results found for "${query}"</div>`;
    return;
  }

  resultsContainer.innerHTML = filtered.map(item => `
    <a href="${item.path}" class="search-result-item" onclick="closeSearch()">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span class="search-result-title">${item.title}</span>
        <span style="font-size: 0.72rem; color: var(--accent-metro); font-weight: 700;">${item.cat}</span>
      </div>
      <div class="search-result-sub">${item.desc}</div>
    </a>
  `).join("");
}

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("searchInput");
  if (input) {
    input.addEventListener("input", (e) => renderSearchResults(e.target.value));
  }

  document.addEventListener("keydown", (e) => {
    if ((e.key === "/" || (e.metaKey && e.key === "k")) && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
      e.preventDefault();
      window.openSearch();
    }
    if (e.key === "Escape") {
      window.closeSearch();
    }
  });

  const modal = document.getElementById("searchModal");
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) window.closeSearch();
    });
  }
});
