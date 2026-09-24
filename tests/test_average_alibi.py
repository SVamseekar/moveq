"""The homepage average-alibi fixture is moveq output, not a typed-in number."""

import json
from pathlib import Path

import numpy as np
import pytest

from moveq_core.equity import compute_concentration_index, compute_gini

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "website" / "assets" / "data" / "average-alibi.json"


def test_average_alibi_fixture_matches_moveq():
    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert doc["rank_direction"] == "higher_is_advantaged"
    population = np.asarray(doc["population"], dtype=float)
    rank = np.asarray(doc["rank"], dtype=float)
    assert [state["id"] for state in doc["states"]] == ["A", "B", "C"]
    means = []
    for state in doc["states"]:
        waits = np.asarray(state["waits"], dtype=float)
        mean = float(np.average(waits, weights=population))
        gini = compute_gini(waits, population)
        ci = compute_concentration_index(
            waits, rank, population, rank_direction="higher_is_advantaged"
        )
        assert state["mean"] == pytest.approx(mean)
        assert state["gini"] == pytest.approx(gini)
        assert state["concentration_index"] == pytest.approx(ci)
        means.append(mean)
    assert means == pytest.approx([24.0, 24.0, 24.0])
    assert doc["states"][0]["gini"] == pytest.approx(0.0)
    assert doc["states"][1]["gini"] == pytest.approx(doc["states"][2]["gini"])
    assert doc["states"][2]["concentration_index"] < doc["states"][1]["concentration_index"]
    assert "disadvantage-concentrated" in doc["states"][2]["diagnosis"]
    assert "unfair" not in json.dumps(doc).lower()
