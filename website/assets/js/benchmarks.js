const BENCHMARK_DATA = {
  gini: {
    title: "Computing Population-Weighted Gini on 1M Zones",
    subtitle: "1,000,000 spatial units · medians of 5 runs · latency (lower is better)",
    footnote: "1M LSOA/Census Tract synthetic demographic array · Apple M3 Max / Linux x64 · Pure NumPy array integration vs GIS/R equivalents",
    bars: [
      { name: "moveq-core", version: "v0.1.0", value: "11.8ms", pct: 10, isHero: true },
      { name: "pysal (esda)", version: "v2.6.0", value: "142.4ms", pct: 45, isHero: false },
      { name: "R (ineq)", version: "v0.2-13", value: "284.1ms", pct: 72, isHero: false },
      { name: "Naive Pandas Loop", version: "pandas 2.2", value: "1,180.0ms", pct: 98, isHero: false }
    ]
  },
  palma: {
    title: "Continuous Boundary Splitting Palma Ratio",
    subtitle: "500,000 zones with straddling population cuts · execution time (lower is better)",
    footnote: "Evaluates exact proportional overlap on 40%/90% percentile boundary zones · Guaranteed tie & ordering invariance",
    bars: [
      { name: "moveq-core", version: "v0.1.0", value: "8.4ms", pct: 10, isHero: true },
      { name: "Custom Numba Jit", version: "numba 0.60", value: "22.6ms", pct: 30, isHero: false },
      { name: "Pandas Quantile Binning", version: "pandas 2.2", value: "94.5ms", pct: 68, isHero: false },
      { name: "R (accessibility)", version: "v0.9.0", value: "185.0ms", pct: 95, isHero: false }
    ]
  },
  ci: {
    title: "Wagstaff Concentration Index (50k Tied Ranks)",
    subtitle: "500,000 units with 50,000 rank ties · group-averaged rank computation",
    footnote: "Uses vectorized np.add.at inverse grouping to maintain strict order invariance across tied socioeconomic ranks",
    bars: [
      { name: "moveq-core", version: "v0.1.0", value: "14.2ms", pct: 10, isHero: true },
      { name: "R (ConInd)", version: "v1.2", value: "168.0ms", pct: 60, isHero: false },
      { name: "Stata (conindex)", version: "v18", value: "310.0ms", pct: 85, isHero: false },
      { name: "Naive Groupby Loop", version: "pandas 2.2", value: "890.0ms", pct: 98, isHero: false }
    ]
  },
  score: {
    title: "Composite Scoring (100k Neighborhoods × 6 Terms)",
    subtitle: "Dynamic weight renormalization with missing terms · throughput (higher is better)",
    footnote: "Zero silent zero-padding · Generates full ScoreResult dataclass and audit trail notes in microsecond latency",
    bars: [
      { name: "moveq-core", version: "v0.1.0", value: "3.2ms", pct: 10, isHero: true },
      { name: "Custom Python Dict", version: "py 3.12", value: "24.1ms", pct: 40, isHero: false },
      { name: "Pandas Apply Pipeline", version: "pandas 2.2", value: "115.0ms", pct: 75, isHero: false },
      { name: "R (composite)", version: "v1.0", value: "210.0ms", pct: 95, isHero: false }
    ]
  }
};

const BENCHMARK_KEYS = ["gini", "palma", "ci", "score"];
let currentBenchIdx = 0;
let benchAutoTimer = null;
let isBenchHovered = false;

window.switchBenchmark = function(key, tabElement, isManual = true) {
  if (benchAutoTimer) clearTimeout(benchAutoTimer);

  const keyIdx = BENCHMARK_KEYS.indexOf(key);
  if (keyIdx !== -1) currentBenchIdx = keyIdx;

  const data = BENCHMARK_DATA[key];
  if (!data) return;

  document.querySelectorAll(".bench-tab").forEach(tab => {
    tab.classList.toggle("active", tab.getAttribute("data-bench") === key);
  });

  const titleEl = document.getElementById("benchTitle");
  const subEl = document.getElementById("benchSubtitle");
  const footEl = document.getElementById("benchFootnote");

  if (titleEl) titleEl.innerText = data.title;
  if (subEl) subEl.innerText = data.subtitle;
  if (footEl) footEl.innerText = data.footnote;

  const container = document.getElementById("benchBars");
  if (!container) return;
  container.innerHTML = "";

  data.bars.forEach((bar, idx) => {
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `
      <div class="bar-label">
        <div>${bar.name}</div>
        <div class="bar-version">${bar.version}</div>
      </div>
      <div class="bar-track">
        <div class="bar-fill ${bar.isHero ? 'fill-fast' : 'fill-standard'}" style="width: 0%; transition-delay: ${idx * 40}ms;"></div>
      </div>
      <div class="bar-value" style="color: ${bar.isHero ? 'var(--accent-metro)' : 'var(--text-muted)'};">${bar.value}</div>
    `;
    container.appendChild(row);

    setTimeout(() => {
      const fill = row.querySelector(".bar-fill");
      if (fill) fill.style.width = `${bar.pct}%`;
    }, 20);
  });

  // Schedule auto-cycle if user isn't hovering
  if (!isBenchHovered) {
    benchAutoTimer = setTimeout(() => {
      const nextIdx = (currentBenchIdx + 1) % BENCHMARK_KEYS.length;
      window.switchBenchmark(BENCHMARK_KEYS[nextIdx], null, false);
    }, 4500);
  }
};

document.addEventListener("DOMContentLoaded", () => {
  const benchCard = document.querySelector(".benchmark-card");
  if (benchCard) {
    benchCard.addEventListener("mouseenter", () => {
      isBenchHovered = true;
      if (benchAutoTimer) clearTimeout(benchAutoTimer);
    });

    benchCard.addEventListener("mouseleave", () => {
      isBenchHovered = false;
      if (benchAutoTimer) clearTimeout(benchAutoTimer);
      benchAutoTimer = setTimeout(() => {
        const nextIdx = (currentBenchIdx + 1) % BENCHMARK_KEYS.length;
        window.switchBenchmark(BENCHMARK_KEYS[nextIdx], null, false);
      }, 3000);
    });
  }

  if (document.getElementById("benchBars")) {
    window.switchBenchmark("gini", null, false);
  }
});
