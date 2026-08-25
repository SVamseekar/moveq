(function() {
  const canvas = document.getElementById("lorenzCanvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const lowIncomeSlider = document.getElementById("lowServiceSlider") || document.getElementById("sliderLowIncome");
  const highIncomeSlider = document.getElementById("highServiceSlider") || document.getElementById("sliderHighIncome");

  function calculateLorenzPoints(lowVal, highVal) {
    const pop = [0.2, 0.2, 0.2, 0.2, 0.2];
    const service = [
      parseFloat(lowVal),
      parseFloat(lowVal) * 1.4,
      (parseFloat(lowVal) + parseFloat(highVal)) / 2,
      parseFloat(highVal) * 0.85,
      parseFloat(highVal)
    ];

    const totalService = service.reduce((acc, s, i) => acc + s * pop[i], 0);

    let cumPop = [0];
    let cumServ = [0];
    let currP = 0, currS = 0;

    for (let i = 0; i < pop.length; i++) {
      currP += pop[i];
      currS += (service[i] * pop[i]) / (totalService || 1);
      cumPop.push(currP);
      cumServ.push(currS);
    }

    let lorenzArea = 0;
    for (let i = 0; i < cumPop.length - 1; i++) {
      const dx = cumPop[i + 1] - cumPop[i];
      const yAvg = (cumServ[i + 1] + cumServ[i]) / 2;
      lorenzArea += dx * yAvg;
    }

    const gini = Math.max(0, Math.min(1, 1 - 2 * lorenzArea));
    const bottom40Mean = (service[0] + service[1]) / 2;
    const top10Mean = service[4];
    const palma = bottom40Mean > 0 ? top10Mean / bottom40Mean : 99.9;

    const meanS = totalService || 1;
    let cov = 0;
    for (let i = 0; i < service.length; i++) {
      const fracRank = (cumPop[i] + cumPop[i + 1]) / 2;
      cov += pop[i] * (service[i] - meanS) * (fracRank - 0.5);
    }
    const ci = (2 * cov) / meanS;

    return { cumPop, cumServ, gini, palma, ci };
  }

  function drawCanvas() {
    const lowVal = lowIncomeSlider ? lowIncomeSlider.value : 5;
    const highVal = highIncomeSlider ? highIncomeSlider.value : 65;

    const lowValLabel = document.getElementById("lowServiceVal");
    const highValLabel = document.getElementById("highServiceVal");
    if (lowValLabel) lowValLabel.innerText = parseFloat(lowVal).toFixed(1);
    if (highValLabel) highValLabel.innerText = parseFloat(highVal).toFixed(1);

    const { cumPop, cumServ, gini, palma, ci } = calculateLorenzPoints(lowVal, highVal);

    const giniEl = document.getElementById("liveGini") || document.getElementById("calcGini");
    const palmaEl = document.getElementById("livePalma") || document.getElementById("calcPalma");
    const ciEl = document.getElementById("liveCi") || document.getElementById("calcCI");

    if (giniEl) giniEl.innerText = gini.toFixed(3);
    if (palmaEl) palmaEl.innerText = palma.toFixed(2);
    if (ciEl) {
      ciEl.innerText = (ci >= 0 ? "+" : "") + ci.toFixed(3);
      ciEl.style.color = ci < 0 ? "var(--accent-emerald)" : "var(--accent-crimson)";
    }

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const w = rect.width;
    const h = rect.height;
    const pad = 36;
    const plotW = w - pad * 2;
    const plotH = h - pad * 2;

    ctx.clearRect(0, 0, w, h);

    // Grid
    ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const x = pad + (plotW * i) / 4;
      const y = pad + (plotH * i) / 4;

      ctx.beginPath();
      ctx.moveTo(x, pad);
      ctx.lineTo(x, h - pad);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(pad, y);
      ctx.lineTo(w - pad, y);
      ctx.stroke();
    }

    // 45-degree line
    ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(pad, h - pad);
    ctx.lineTo(w - pad, pad);
    ctx.stroke();
    ctx.setLineDash([]);

    // Shaded Area
    ctx.fillStyle = "rgba(56, 189, 248, 0.15)";
    ctx.beginPath();
    ctx.moveTo(pad, h - pad);
    for (let i = 0; i < cumPop.length; i++) {
      const px = pad + cumPop[i] * plotW;
      const py = h - pad - cumServ[i] * plotH;
      ctx.lineTo(px, py);
    }
    ctx.lineTo(w - pad, h - pad);
    ctx.closePath();
    ctx.fill();

    // Lorenz Curve
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 3;
    ctx.beginPath();
    for (let i = 0; i < cumPop.length; i++) {
      const px = pad + cumPop[i] * plotW;
      const py = h - pad - cumServ[i] * plotH;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();

    // Data points
    for (let i = 0; i < cumPop.length; i++) {
      const px = pad + cumPop[i] * plotW;
      const py = h - pad - cumServ[i] * plotH;
      ctx.fillStyle = "#38bdf8";
      ctx.beginPath();
      ctx.arc(px, py, 4, 0, Math.PI * 2);
      ctx.fill();
    }

    // Axis Labels
    ctx.fillStyle = "rgba(255, 255, 255, 0.5)";
    ctx.font = "10px monospace";
    ctx.fillText("0%", pad - 20, h - pad + 4);
    ctx.fillText("100%", w - pad - 12, h - pad + 16);
    ctx.fillText("Population →", pad + plotW / 3, h - pad + 24);
  }

  if (lowIncomeSlider && highIncomeSlider) {
    lowIncomeSlider.addEventListener("input", drawCanvas);
    highIncomeSlider.addEventListener("input", drawCanvas);
    window.addEventListener("resize", drawCanvas);
    drawCanvas();
  }
})();
