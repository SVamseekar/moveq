"""Missing-data ranking fixture is compute_score output."""

import json
from pathlib import Path

import pytest

from moveq_core.score import compute_score

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "website" / "assets" / "data" / "missing-data.json"


def test_missing_data_fixture_matches_moveq():
    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    weights = doc["weights"]
    assert set(doc["policies"]) == {"reweight", "as_zero", "exclude", "bounds"}
    east = {}
    for policy, rows in doc["policies"].items():
        for row in rows:
            result = compute_score(row["terms"], weights, missing_policy=policy)
            assert row["score"] == pytest.approx(result.score) if result.score is not None else row["score"] is None
            if result.bounds is None:
                assert row["bounds"] is None
            else:
                assert row["bounds"][0] == pytest.approx(result.bounds[0])
                assert row["bounds"][1] == pytest.approx(result.bounds[1])
            if row["name"] == "East":
                east[policy] = row
    assert east["reweight"]["score"] == pytest.approx(73.33333333333333)
    assert east["as_zero"]["score"] == pytest.approx(55.0)
    assert east["exclude"]["score"] is None
    assert east["bounds"]["score"] is None
    assert east["bounds"]["bounds"][0] == pytest.approx(55.0)
    assert east["bounds"]["bounds"][1] == pytest.approx(80.0)
    reweight_order = [
        row["name"]
        for row in sorted(doc["policies"]["reweight"], key=lambda row: -row["score"])
    ]
    zero_order = [
        row["name"]
        for row in sorted(doc["policies"]["as_zero"], key=lambda row: -row["score"])
    ]
    assert reweight_order.index("East") < reweight_order.index("South")
    assert zero_order.index("South") < zero_order.index("East")
