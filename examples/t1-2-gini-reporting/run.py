"""Chart the synthetic service array already in examples/basic_equity.

No external extract. Writes one SVG thumbnail for the gallery card.

    python examples/t1-2-gini-reporting/run.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from moveq import compute_gini

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "examples" / "basic_equity" / "data.csv"
OUT = ROOT / "website" / "examples" / "thumbnails" / "t1-2-gini-reporting.svg"


def load() -> tuple[np.ndarray, np.ndarray]:
    with DATA.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    trips = np.array([float(row["trips"]) for row in rows])
    population = np.array([float(row["population"]) for row in rows])
    return trips, population


def write_svg(trips: np.ndarray) -> None:
    width, height, pad = 320, 180, 16
    peak = float(trips.max())
    bars = []
    slot = (width - 2 * pad) / len(trips)
    for index, value in enumerate(trips):
        bar_h = (float(value) / peak) * (height - 2 * pad)
        x = pad + index * slot + 4
        y = height - pad - bar_h
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{slot - 8:.1f}" height="{bar_h:.1f}" fill="#38bdf8"/>'
        )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180" role="img" '
        'aria-label="Trips per area">'
        '<rect width="320" height="180" fill="#0f172a"/>'
        + "".join(bars)
        + "</svg>\n"
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")


def main() -> None:
    trips, population = load()
    gini = compute_gini(trips, population)
    write_svg(trips)
    print(f"Gini: {gini:.4f}")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
