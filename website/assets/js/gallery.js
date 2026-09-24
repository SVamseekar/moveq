(function () {
  const root = document.getElementById("gallery");
  if (!root) return;
  const fieldSelect = document.getElementById("galleryField");
  const badgeSelect = document.getElementById("galleryBadge");
  const researchList = document.getElementById("galleryResearch");
  const everydayList = document.getElementById("galleryEveryday");

  function option(select, value) {
    const el = document.createElement("option");
    el.value = value;
    el.textContent = value;
    select.append(el);
  }

  function thumb(card) {
    const img = document.createElement("img");
    img.alt = card.question;
    img.src = card.thumbnail || "/examples/thumbnails/pending.svg";
    return img;
  }

  function badge(card) {
    const span = document.createElement("span");
    span.className = "gallery-badge";
    span.textContent = card.badge;
    return span;
  }

  function researchCard(card) {
    const article = document.createElement("article");
    article.className = "gallery-card gallery-card-research";
    article.dataset.field = card.field;
    article.dataset.badge = card.badge;
    const spec = document.createElement("p");
    spec.className = "gallery-spec";
    spec.textContent = card.spec + " · " + card.field;
    const title = document.createElement("h3");
    title.textContent = card.question;
    article.append(thumb(card), spec, title, badge(card));
    return article;
  }

  function everydayCard(card) {
    const article = document.createElement("article");
    article.className = "gallery-card gallery-card-everyday";
    article.dataset.field = card.field;
    article.dataset.badge = card.badge;
    const title = document.createElement("h3");
    title.textContent = card.question;
    const situation = document.createElement("p");
    situation.textContent = card.thumbnail
      ? "A synthetic illustration of hours. No external extract."
      : "Not runnable yet. No extract: the licence is not confirmed.";
    article.append(thumb(card), title, situation, badge(card));
    return article;
  }

  function apply() {
    const field = fieldSelect.value;
    const claim = badgeSelect.value;
    root.querySelectorAll(".gallery-card").forEach((card) => {
      const show = (field === "all" || card.dataset.field === field)
        && (claim === "all" || card.dataset.badge === claim);
      card.hidden = !show;
    });
  }

  fetch("/assets/data/gallery.json")
    .then((res) => res.json())
    .then((doc) => {
      const research = doc.tiers.find((tier) => tier.id === "research");
      const everyday = doc.tiers.find((tier) => tier.id === "everyday");
      const fields = new Set();
      const badges = new Set();
      research.cards.forEach((card) => {
        fields.add(card.field);
        badges.add(card.badge);
        researchList.append(researchCard(card));
      });
      everyday.cards.forEach((card) => {
        fields.add(card.field);
        badges.add(card.badge);
        everydayList.append(everydayCard(card));
      });
      [...fields].sort().forEach((value) => option(fieldSelect, value));
      [...badges].sort().forEach((value) => option(badgeSelect, value));
      fieldSelect.addEventListener("change", apply);
      badgeSelect.addEventListener("change", apply);
    });
})();
