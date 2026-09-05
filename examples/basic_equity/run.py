"""End-to-end demo: equity metrics + a composite score + a catalogue check.

Run from the repo root after installing the packages (see README):

    python examples/basic_equity/run.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from moveq import (
    Catalogue,
    SectionAction,
    compute_concentration_index,
    compute_gini,
    compute_palma_ratio,
    compute_score,
)

DATA_PATH = Path(__file__).parent / "data.csv"


def load_columns() -> dict[str, np.ndarray]:
    with open(DATA_PATH, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {
        "trips": np.array([float(r["trips"]) for r in rows]),
        "population": np.array([float(r["population"]) for r in rows]),
        "deprivation_rank": np.array([float(r["deprivation_rank"]) for r in rows]),
    }


def main() -> None:
    cols = load_columns()

    gini = compute_gini(cols["trips"], cols["population"])
    palma = compute_palma_ratio(cols["trips"], cols["population"])
    ci = compute_concentration_index(
        cols["trips"],
        cols["deprivation_rank"],
        cols["population"],
        rank_direction="higher_is_advantaged",
    )

    print(f"Gini:                  {gini:.4f}")
    print(f"Palma ratio:           {palma:.4f}")
    print(f"Concentration Index:   {ci:.4f}")

    score = compute_score(
        terms={"coverage": 0.72, "evening": 0.55, "frequency": None, "gap": 1 - abs(ci)},
        weights={"coverage": 0.40, "evening": 0.25, "frequency": 0.20, "gap": 0.15},
        labels={
            "coverage": "Share within 400m",
            "evening": "Evening service share",
            "frequency": "Weekday frequency",
            "gap": "Deprivation-service gap (inverted)",
        },
        n_areas=len(cols["trips"]),
    )
    print(f"\nComposite score: {score.score:.1f} ({score.note})")

    base_sections = ["coverage_pct", "service_deserts", "policy_scenarios"]
    catalogue = Catalogue(base_sections, country="example-country")
    catalogue.register("coverage_pct", SectionAction.SAME, note="local GTFS x local census unit")
    catalogue.register("service_deserts", SectionAction.SAME)
    catalogue.register(
        "policy_scenarios",
        SectionAction.REPLACE,
        replacement_title="Local transport strategy scenarios",
    )
    issues = catalogue.validate()
    print(f"\nCatalogue summary: {catalogue.summary()}")
    print("Catalogue fully specified." if not issues else f"Catalogue issues: {issues}")


if __name__ == "__main__":
    main()
