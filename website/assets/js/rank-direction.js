(function () {
  const root = document.getElementById("rank-direction");
  if (!root) return;
  const valueEl = document.getElementById("rankDirectionValue");
  const note = document.getElementById("rankDirectionNote");
  const buttons = root.querySelectorAll("[data-direction]");

  function fmt(value) {
    const text = Number(value).toFixed(3);
    return value > 0 ? "+" + text : text;
  }

  function show(data, direction) {
    const value = data.directions[direction];
    valueEl.textContent = fmt(value);
    if (direction === "higher_is_advantaged") {
      note.textContent = "Same service, same rank, same population. Declaring that a higher rank is advantaged gives " + fmt(value) + ". The argument is required. There is no default, because the other declaration flips the sign.";
    } else {
      note.textContent = "The arrays did not change. Declaring that a higher rank is disadvantaged gives " + fmt(value) + ". moveq will not guess which end is advantaged. Omitting rank_direction is a TypeError.";
    }
  }

  fetch("/assets/data/rank-direction.json")
    .then((res) => {
      if (!res.ok) throw new Error("fixture missing");
      return res.json();
    })
    .then((data) => {
      buttons.forEach((button) => {
        button.addEventListener("click", () => {
          buttons.forEach((other) => other.classList.remove("active"));
          button.classList.add("active");
          show(data, button.getAttribute("data-direction"));
        });
      });
      show(data, "higher_is_advantaged");
    })
    .catch(() => {
      note.textContent = "The precomputed moveq fixture did not load.";
    });
})();
