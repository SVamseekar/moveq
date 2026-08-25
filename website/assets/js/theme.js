(function() {
  const storedTheme = localStorage.getItem("moveq-theme") || 
    (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", storedTheme);

  window.toggleTheme = function() {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("moveq-theme", next);
    updateThemeIcon(next);
  };

  function updateThemeIcon(theme) {
    const btn = document.getElementById("themeToggleBtn");
    if (!btn) return;
    btn.innerHTML = theme === "dark" 
      ? `<svg class="icon" width="18" height="18" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>`
      : `<svg class="icon" width="18" height="18" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
  }

  document.addEventListener("DOMContentLoaded", () => {
    updateThemeIcon(document.documentElement.getAttribute("data-theme"));
  });

  window.copyText = function(text, btnElement) {
    navigator.clipboard.writeText(text).then(() => {
      const orig = btnElement.innerHTML;
      btnElement.innerHTML = `✓ Copied`;
      setTimeout(() => {
        btnElement.innerHTML = orig;
      }, 2000);
    });
  };

  window.copyInstallerCmd = function(btnElement) {
    const cmdEl = document.getElementById("installerCmd");
    if (!cmdEl) return;
    window.copyText(cmdEl.innerText, btnElement);
  };

  window.switchInstaller = function(type, tabElement) {
    document.querySelectorAll(".installer-tab").forEach(t => t.classList.remove("active"));
    if (tabElement) tabElement.classList.add("active");

    const cmdEl = document.getElementById("installerCmd");
    if (!cmdEl) return;

    let cmd = 'pip install "moveq[cli,frames]"';
    if (type === "uv") cmd = 'uv add "moveq[cli,frames]"';
    else if (type === "conda") cmd = 'conda install -c conda-forge moveq';
    else if (type === "core" || type === "pip-core") cmd = 'pip install moveq-core';

    cmdEl.innerText = cmd;
  };
})();
