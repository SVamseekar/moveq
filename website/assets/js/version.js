/**
 * Real-time GitHub Release Sync for moveq
 * Fetches the latest release from GitHub API and updates version pills & buttons.
 * Uses localStorage cache with 5-minute TTL to stay fast and avoid rate limits.
 */
(function() {
  const REPO = "SVamseekar/moveq";
  const CACHE_KEY = "moveq_github_latest_release";
  const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

  async function fetchLatestRelease() {
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      if (cached) {
        const parsed = JSON.parse(cached);
        if (Date.now() - parsed.timestamp < CACHE_TTL) {
          applyReleaseData(parsed.data);
          return;
        }
      }
    } catch (e) {}

    try {
      const res = await fetch(`https://api.github.com/repos/${REPO}/releases/latest`, {
        headers: { "Accept": "application/vnd.github.v3+json" }
      });

      if (res.ok) {
        const data = await res.json();
        const releaseData = {
          tag: data.tag_name || "v0.1.1",
          name: data.name || "",
          url: data.html_url || `https://github.com/${REPO}/releases`,
          publishedAt: data.published_at
        };

        try {
          localStorage.setItem(CACHE_KEY, JSON.stringify({
            timestamp: Date.now(),
            data: releaseData
          }));
        } catch (e) {}

        applyReleaseData(releaseData);
        return;
      }

      // Fallback: Check tags
      const tagRes = await fetch(`https://api.github.com/repos/${REPO}/tags`, {
        headers: { "Accept": "application/vnd.github.v3+json" }
      });

      if (tagRes.ok) {
        const tags = await tagRes.json();
        if (tags && tags.length > 0) {
          const releaseData = {
            tag: tags[0].name,
            name: "",
            url: `https://github.com/${REPO}/releases/tag/${tags[0].name}`,
            publishedAt: null
          };
          applyReleaseData(releaseData);
        }
      }
    } catch (err) {
      console.debug("GitHub release check fallback:", err);
    }
  }

  function applyReleaseData(rel) {
    if (!rel || !rel.tag) return;

    // 1. Clean Title Formatting (prevents "v0.1.1 — v0.1.1 Released")
    let extraTitle = "";
    if (rel.name && rel.name.trim() !== rel.tag.trim()) {
      let clean = rel.name.replace(new RegExp(`^${rel.tag}\\s*[-—:]*\\s*`, "i"), "").trim();
      if (clean) {
        extraTitle = ` — ${clean}`;
      }
    }

    // 2. Update Hero Release Pill
    const pill = document.getElementById("latestReleasePill");
    const pillText = document.getElementById("releasePillText");
    if (pillText) {
      pillText.innerText = `${rel.tag}${extraTitle} Released →`;
    }
    if (pill && rel.url) {
      pill.href = rel.url;
      pill.target = "_blank";
      pill.rel = "noopener noreferrer";
    }

    // 3. Update Header Install Cut Buttons
    document.querySelectorAll(".header-version-text, .cut-btn span").forEach(el => {
      if (el.innerText.toLowerCase().includes("install")) {
        el.innerText = `Install ${rel.tag}`;
      }
    });

    // 4. Update any version badges
    document.querySelectorAll("[data-github-version]").forEach(el => {
      el.innerText = rel.tag;
    });
  }

  // Clear cache if version is forced or stale
  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (cached) {
      const parsed = JSON.parse(cached);
      applyReleaseData(parsed.data);
    }
  } catch (e) {}

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", fetchLatestRelease);
  } else {
    fetchLatestRelease();
  }
})();
