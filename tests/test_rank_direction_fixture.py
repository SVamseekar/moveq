"""Rank-direction homepage fixture is compute_concentration_index output."""

import json
from pathlib import Path

import numpy as np
import pytest

from moveq_core.equity import compute_concentration_index

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "website" / "assets" / "data" / "rank-direction.json"


def test_rank_direction_fixture_flips_sign():
    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    service = np.asarray(doc["service"], dtype=float)
    rank = np.asarray(doc["rank"], dtype=float)
    population = np.asarray(doc["population"], dtype=float)
    adv = compute_concentration_index(
        service, rank, population, rank_direction="higher_is_advantaged"
    )
    dis = compute_concentration_index(
        service, rank, population, rank_direction="higher_is_disadvantaged"
    )
    assert doc["directions"]["higher_is_advantaged"] == pytest.approx(adv)
    assert doc["directions"]["higher_is_disadvantaged"] == pytest.approx(dis)
    assert adv == pytest.approx(0.25)
    assert dis == pytest.approx(-0.25)
    assert dis == pytest.approx(-adv)
