const TOUR_STATIONS = [
  {
    num: "01",
    title: "Calculate Population-Weighted Gini",
    desc: "Evaluate city-wide transit service inequality directly from spatial CSV rows.",
    cmd: "moveq gini data.csv --value trips --weight population",
    output: [
      "[INFO] Ingesting 5 spatial census zones (pop = 4,200)",
      "[INFO] Lorenz integration area: 0.3049",
      "",
      "gini: 0.3902"
    ]
  },
  {
    num: "02",
    title: "Compute Continuous Palma Ratio",
    desc: "Inspect top 10% vs bottom 40% extremes with boundary polygon splitting.",
    cmd: "moveq palma data.csv --value trips --weight population",
    output: [
      "[INFO] Proportional boundary cut @ 40th & 90th percentiles",
      "[CALC] Top-10% mean: 50.0 trips | Bottom-40% mean: 7.07 trips",
      "",
      "palma: 7.0732"
    ]
  },
  {
    num: "03",
    title: "Evaluate Concentration Index",
    desc: "Audit whether transit access favors deprived or affluent demographic tracts.",
    cmd: "moveq ci data.csv --value trips --rank deprivation_rank --weight population",
    output: [
      "[INFO] Group-averaged fractional rank calculation for tied deciles",
      "[STATUS] Positive = Pro-Rich disparity (+2.019 cov)",
      "",
      "concentration_index: +0.2457  (favors less deprived areas)"
    ]
  },
  {
    num: "04",
    title: "Dynamic Composite Scoring",
    desc: "Drop missing indicators and renormalize active weights dynamically.",
    cmd: "moveq score --terms '{\"coverage\": 0.8, \"evening\": 0.5}' --weights '{\"coverage\": 0.6, \"evening\": 0.4, \"night\": 0.2}'",
    output: [
      "[WARN] Indicator 'night' not present — weight dropped",
      "[INFO] Dynamic renormalization: coverage (0.60), evening (0.40)",
      "",
      "score: 68.0 / 100.0",
      "note: night service not in this cut — weights renormalised."
    ]
  },
  {
    num: "05",
    title: "Validate Harmonization Catalogue",
    desc: "Ensure cross-country questionnaire adaptations preserve full methodology.",
    cmd: "moveq catalogue validate france_catalogue.json",
    output: [
      "country: France (FR)",
      "mappings: bus_coverage (same), evening (same), imd (replace)",
      "summary: same=2, replace=1, omit=0",
      "",
      "status: valid (100% harmonized contract)"
    ]
  }
];

let activeIndex = 0;
let typingTimer = null;
let advanceTimer = null;
let isUserHovering = false;
let hasStarted = false;

function clearTimers() {
  if (typingTimer) clearTimeout(typingTimer);
  if (advanceTimer) clearTimeout(advanceTimer);
  typingTimer = null;
  advanceTimer = null;
}

window.selectStation = function(idx, manual = true) {
  clearTimers();
  activeIndex = idx;

  const station = TOUR_STATIONS[idx];
  if (!station) return;

  // Update station list active states
  const stationElements = document.querySelectorAll(".station-item");
  stationElements.forEach((el, i) => {
    el.classList.toggle("active", i === idx);
  });

  const cmdEl = document.getElementById("terminalCmd");
  const outEl = document.getElementById("terminalOutput");
  if (!cmdEl || !outEl) return;

  cmdEl.innerHTML = `<span class="term-cursor">_</span>`;
  outEl.innerText = "";

  // Smooth left-aligned character-by-character typing
  let pos = 0;
  function typeChar() {
    if (pos <= station.cmd.length) {
      cmdEl.innerHTML = station.cmd.slice(0, pos) + `<span class="term-cursor">_</span>`;
      pos++;
      typingTimer = setTimeout(typeChar, 10);
    } else {
      cmdEl.innerHTML = station.cmd;
      typingTimer = setTimeout(() => {
        outEl.innerText = station.output.join("\n");

        if (!isUserHovering) {
          advanceTimer = setTimeout(() => {
            const nextIdx = (activeIndex + 1) % TOUR_STATIONS.length;
            window.selectStation(nextIdx, false);
          }, 4000);
        }
      }, 100);
    }
  }

  typeChar();
};

document.addEventListener("DOMContentLoaded", () => {
  const tourSection = document.querySelector(".tour-section");
  if (!tourSection) return;

  tourSection.addEventListener("mouseenter", () => {
    isUserHovering = true;
    if (advanceTimer) clearTimeout(advanceTimer);
  });

  tourSection.addEventListener("mouseleave", () => {
    isUserHovering = false;
    if (advanceTimer) clearTimeout(advanceTimer);
    advanceTimer = setTimeout(() => {
      const nextIdx = (activeIndex + 1) % TOUR_STATIONS.length;
      window.selectStation(nextIdx, false);
    }, 2000);
  });

  // Start at Station 01 ONLY when the user scrolls it into view
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !hasStarted) {
          hasStarted = true;
          window.selectStation(0, false);
        }
      });
    }, { threshold: 0.25 });
    observer.observe(tourSection);
  } else {
    window.selectStation(0, false);
  }
});
