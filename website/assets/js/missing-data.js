(function () {
  const root = document.getElementById("missing-data");
  if (!root) return;

  const list = document.getElementById("missingRank");
  const note = document.getElementById("missingNote");
  const buttons = root.querySelectorAll("[data-policy]");

  function fmt(value) {
    return Number(value).toFixed(2);
  }

  function show(data, policy) {
    const rows = data.policies[policy].slice();
    rows.sort((a, b) => {
      const as = a.score === null ? -1 : a.score;
      const bs = b.score === null ? -1 : b.score;
      return bs - as;
    });
    list.replaceChildren();
    rows.forEach((row, index) => {
      const item = document.createElement("li");
      const name = document.createElement("span");
      name.textContent = row.name;
      const score = document.createElement("span");
      if (row.score === null && row.bounds) {
        score.textContent = fmt(row.bounds[0]) + "–" + fmt(row.bounds[1]);
      } else if (row.score === null) {
        score.textContent = "no score";
      } else {
        score.textContent = fmt(row.score);
      }
      item.append(name, score);
      if (row.score === null) item.className = "missing-unranked";
      else name.prepend(document.createTextNode(index + 1 + ". "));
      list.append(item);
    });
    const east = data.policies[policy].find((row) => row.name === "East");
    if (policy === "bounds") {
      note.textContent = "Bounds is the honest option under uncertainty. East has no point score. The interval is " + fmt(east.bounds[0]) + " to " + fmt(east.bounds[1]) + ", and it overlaps South. Reweighting is one declared policy, not the proper one.";
    } else if (policy === "exclude") {
      note.textContent = "Exclude returns no score for East because climate is missing. The other three keep their complete-data scores. Reweighting is one declared policy, not the proper one.";
    } else if (policy === "as_zero") {
      note.textContent = "Treating East's missing climate term as zero scores East at " + fmt(east.score) + ". South, at 65.00, now ranks above East. Reweighting is one declared policy, not the proper one.";
    } else {
      note.textContent = "Reweighting drops East's missing climate term and renormalises the rest, scoring East at " + fmt(east.score) + ". That places East above South. Reweighting is one declared policy, not the proper one.";
    }
  }

  fetch("/assets/data/missing-data.json")
    .then((res) => {
      if (!res.ok) throw new Error("fixture missing");
      return res.json();
    })
    .then((data) => {
      buttons.forEach((button) => {
        button.addEventListener("click", () => {
          buttons.forEach((other) => other.classList.remove("active"));
          button.classList.add("active");
          show(data, button.getAttribute("data-policy"));
        });
      });
      show(data, "reweight");
    })
    .catch(() => {
      note.textContent = "The precomputed moveq fixture did not load.";
    });
})();
