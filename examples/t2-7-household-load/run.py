"""Synthetic household hours. No external extract.

    python examples/t2-7-household-load/run.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from moveq import compute_gini

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "website" / "examples" / "thumbnails" / "t2-7-household-load.svg"

# Four people. Three do six hours. One does eighteen. Constructed.
HOURS = np.array([6.0, 6.0, 6.0, 18.0])
PEOPLE = np.ones(4)


def write_svg(hours: np.ndarray) -> None:
    width, height, pad = 320, 180, 16
    peak = float(hours.max())
    slot = (width - 2 * pad) / len(hours)
    bars = []
    for index, value in enumerate(hours):
        bar_h = (float(value) / peak) * (height - 2 * pad)
        x = pad + index * slot + 8
        y = height - pad - bar_h
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{slot - 16:.1f}" height="{bar_h:.1f}" fill="#34d399"/>'
        )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180" role="img" '
        'aria-label="Hours per person">'
        '<rect width="320" height="180" fill="#0f172a"/>'
        + "".join(bars)
        + "</svg>\n"
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")


def main() -> None:
    gini = compute_gini(HOURS, PEOPLE)
    write_svg(HOURS)
    print(f"Gini: {gini:.4f}")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
