(function () {
  const root = document.getElementById("average-alibi");
  if (!root) return;

  const slider = document.getElementById("alibiSlider");
  const bars = document.getElementById("alibiBars");
  const title = document.getElementById("alibiTitle");
  const diagnosis = document.getElementById("alibiDiagnosis");
  const meanEl = document.getElementById("alibiMean");
  const giniEl = document.getElementById("alibiGini");
  const ciEl = document.getElementById("alibiCi");

  function fmt(value) {
    const n = Number(value);
    if (Object.is(n, -0) || n === 0) return "0";
    return n.toFixed(4).replace(/0+$/, "").replace(/\.$/, "");
  }

  function render(data, index) {
    const state = data.states[index];
    title.textContent = state.title;
    diagnosis.textContent = state.diagnosis;
    meanEl.textContent = fmt(state.mean);
    giniEl.textContent = fmt(state.gini);
    const ci = Number(state.concentration_index);
    ciEl.textContent = (ci > 0 ? "+" : "") + fmt(ci);
    const maxWait = 105;
    bars.innerHTML = state.waits.map((wait, i) => {
      const height = Math.max(4, (wait / maxWait) * 100);
      return `<div class="alibi-col"><div class="alibi-bar" style="height:${height}%"></div><span>${data.rank[i]}</span></div>`;
    }).join("");
  }

  fetch("/assets/data/average-alibi.json")
    .then((res) => {
      if (!res.ok) throw new Error("fixture missing");
      return res.json();
    })
    .then((data) => {
      const paint = () => render(data, Number(slider.value));
      slider.addEventListener("input", paint);
      paint();
    })
    .catch(() => {
      diagnosis.textContent = "The precomputed moveq fixture did not load.";
    });
})();
