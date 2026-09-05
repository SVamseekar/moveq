"""Rank-direction contract for the Concentration Index.

Expected values are closed-form (equal-weight fractional ranks) or oracle
comparisons after an explicit rank-key transform — never the production
function calling itself.
"""

from __future__ import annotations

import numpy as np
import pytest

from moveq_core import (
    compute_concentration_index,
    concentration_index_result,
)
from oracles import concentration_index_grouped

_ADV = "higher_is_advantaged"
_DIS = "higher_is_disadvantaged"


def _closed_form_equal_weight_ci() -> float:
    # n=4, y = 10,20,30,40, equal population. R_i = (i - 0.5)/4.
    # y−μ = [−15,−5,5,15], R−0.5 = [−0.375,−0.125,0.125,0.375]
    # mean of products = 3.125; CI = 2 × 3.125 / 25 = 0.25
    return 0.25


def test_rank_direction_invariance_closed_form():
    service = np.array([10.0, 20.0, 30.0, 40.0])
    population = np.array([100.0, 100.0, 100.0, 100.0])
    expected = _closed_form_equal_weight_ci()
    a = compute_concentration_index(
        service, np.array([1.0, 2.0, 3.0, 4.0]), population, rank_direction=_ADV
    )
    b = compute_concentration_index(
        service, np.array([4.0, 3.0, 2.0, 1.0]), population, rank_direction=_DIS
    )
    assert a == pytest.approx(expected, abs=1e-12)
    assert b == pytest.approx(expected, abs=1e-12)
    assert a == pytest.approx(b, abs=1e-12)


def test_rank_direction_invariance_non_integer_ranks():
    service = np.array([10.0, 20.0, 30.0, 40.0])
    population = np.array([100.0, 100.0, 100.0, 100.0])
    a = compute_concentration_index(
        service, np.array([0.1, 2.5, 7.0, 11.0]), population, rank_direction=_ADV
    )
    b = compute_concentration_index(
        service, np.array([11.0, 7.0, 2.5, 0.1]), population, rank_direction=_DIS
    )
    assert a == pytest.approx(b, abs=1e-12)


def test_wrong_direction_flips_sign():
    service = np.array([10.0, 20.0, 30.0, 40.0])
    rank = np.array([1.0, 2.0, 3.0, 4.0])
    population = np.array([100.0, 100.0, 100.0, 100.0])
    correct = compute_concentration_index(
        service, rank, population, rank_direction=_ADV
    )
    wrong = compute_concentration_index(
        service, rank, population, rank_direction=_DIS
    )
    assert wrong == pytest.approx(-correct, abs=1e-12)


def test_ties_survive_direction_transform():
    service = np.array([10.0, 2.0, 5.0])
    rank = np.array([1.0, 1.0, 2.0])
    population = np.array([50.0, 150.0, 200.0])
    a = compute_concentration_index(service, rank, population, rank_direction=_ADV)
    b = compute_concentration_index(service, -rank, population, rank_direction=_DIS)
    assert a == pytest.approx(b, abs=1e-12)
    assert a == pytest.approx(concentration_index_grouped(service, rank, population), abs=1e-12)


def test_parameters_record_direction():
    service = np.array([1.0, 2.0, 3.0])
    rank = np.array([1.0, 2.0, 3.0])
    population = np.array([1.0, 1.0, 1.0])
    adv = concentration_index_result(service, rank, population, rank_direction=_ADV)
    dis = concentration_index_result(service, rank, population, rank_direction=_DIS)
    assert adv.parameters["rank_direction_input"] == _ADV
    assert adv.parameters["rank_direction_canonical"] == _ADV
    assert adv.parameters["rank_transformed"] is False
    assert dis.parameters["rank_direction_input"] == _DIS
    assert dis.parameters["rank_direction_canonical"] == _ADV
    assert dis.parameters["rank_transformed"] is True
    assert adv.parameters["zero_mean_rtol"] == pytest.approx(1e-9)


def test_omitting_rank_direction_is_type_error():
    with pytest.raises(TypeError):
        compute_concentration_index(
            np.array([1.0, 2.0]), np.array([1.0, 2.0]), np.array([1.0, 1.0])
        )


def test_invalid_rank_direction_is_value_error():
    with pytest.raises(ValueError, match="higher_is_advantaged"):
        compute_concentration_index(
            np.array([1.0, 2.0]),
            np.array([1.0, 2.0]),
            np.array([1.0, 1.0]),
            rank_direction="upside_down",  # type: ignore[arg-type]
        )


def test_permutation_invariance_both_directions():
    rng = np.random.default_rng(11)
    service = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    rank = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    population = np.array([100.0, 80.0, 60.0, 40.0, 20.0])
    perm = rng.permutation(service.size)
    for direction in (_ADV, _DIS):
        base = compute_concentration_index(
            service, rank, population, rank_direction=direction
        )
        shuffled = compute_concentration_index(
            service[perm], rank[perm], population[perm], rank_direction=direction
        )
        assert shuffled == pytest.approx(base, abs=1e-12)
