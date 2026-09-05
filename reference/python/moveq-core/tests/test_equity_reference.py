"""Production metrics must match independent implementations of the docs."""

import numpy as np
import pytest

from moveq_core import compute_concentration_index, compute_gini, compute_palma_ratio

from oracles import (
    concentration_index_grouped,
    finite_or_equal,
    gini_pairwise,
    palma_split_loop,
)

CASES = [
    (np.array([10.0, 10.0, 10.0, 10.0]), np.array([100.0, 100.0, 100.0, 100.0])),
    (np.array([0.0, 1.0]), np.array([1.0, 1.0])),
    (np.array([0.0, 0.0, 0.0, 100.0]), np.array([100.0, 100.0, 100.0, 100.0])),
    (np.array([5.0, 20.0, 1.0, 50.0]), np.array([900.0, 800.0, 1200.0, 300.0])),
    (np.array([0.0, 0.0, 0.0, 0.0]), np.array([100.0, 100.0, 100.0, 100.0])),
    (np.array([1.0, 10.0, 2.0, 2.0]), np.array([30.0, 10.0, 30.0, 30.0])),
    (np.array([1.0, 2.0, 10.0, 100.0]), np.array([40.0, 40.0, 15.0, 5.0])),
    (np.array([0.0, 0.0, 0.0, 0.0, 10.0]), np.array([40.0, 20.0, 20.0, 10.0, 10.0])),
    (np.array([3.0]), np.array([50.0])),
]


@pytest.mark.parametrize("values, weights", CASES)
def test_gini_matches_pairwise_formula(values, weights):
    got = compute_gini(values, weights)
    expected = gini_pairwise(values, weights)
    assert got == pytest.approx(expected, rel=1e-9, abs=1e-12)


@pytest.mark.parametrize("values, weights", CASES)
def test_palma_matches_explicit_split_loop(values, weights):
    got = compute_palma_ratio(values, weights)
    expected = palma_split_loop(values, weights)
    assert finite_or_equal(got, expected)


def test_gini_two_unit_closed_form():
    # Equal-weight two-person Lorenz: area 0.25, G = 0.5. Pairwise agrees.
    values = np.array([0.0, 1.0])
    weights = np.array([1.0, 1.0])
    assert gini_pairwise(values, weights) == pytest.approx(0.5, abs=1e-12)
    assert compute_gini(values, weights) == pytest.approx(0.5, abs=1e-12)


def test_gini_extreme_closed_form():
    # Equal weights, all service in one of n units: G = (n − 1) / n.
    values = np.array([0.0, 0.0, 0.0, 100.0])
    weights = np.array([100.0, 100.0, 100.0, 100.0])
    assert gini_pairwise(values, weights) == pytest.approx(0.75, abs=1e-12)
    assert compute_gini(values, weights) == pytest.approx(0.75, abs=1e-12)


def test_palma_boundary_split_closed_form():
    values = np.array([1.0, 10.0, 2.0, 2.0])
    weights = np.array([30.0, 10.0, 30.0, 30.0])
    expected = 10.0 / 1.25
    assert palma_split_loop(values, weights) == pytest.approx(expected, rel=1e-9)
    assert compute_palma_ratio(values, weights) == pytest.approx(expected, rel=1e-9)


def test_concentration_index_equal_weight_closed_form():
    # n=5, equal population, y = 1..5, R_i = (i − 0.5)/5, cov = 0.4, μ = 3.
    service = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    rank = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    population = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
    expected = 0.8 / 3.0
    assert concentration_index_grouped(service, rank, population) == pytest.approx(expected, abs=1e-12)
    assert compute_concentration_index(
        service, rank, population, rank_direction="higher_is_advantaged"
    ) == pytest.approx(expected, abs=1e-12)


def test_concentration_index_tied_ranks_match_grouped_oracle():
    service = np.array([10.0, 2.0, 5.0])
    rank = np.array([1.0, 1.0, 2.0])
    population = np.array([50.0, 150.0, 200.0])
    got = compute_concentration_index(
        service, rank, population, rank_direction="higher_is_advantaged"
    )
    expected = concentration_index_grouped(service, rank, population)
    assert got == pytest.approx(expected, abs=1e-12)


def test_concentration_index_negative_mean_matches_grouped_oracle():
    service = np.array([-5.0, -4.0, -3.0, -2.0, -1.0])
    rank = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    population = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
    got = compute_concentration_index(
        service, rank, population, rank_direction="higher_is_advantaged"
    )
    expected = concentration_index_grouped(service, rank, population)
    assert got == pytest.approx(expected, abs=1e-12)
    assert expected == pytest.approx(-0.8 / 3.0, abs=1e-12)


def test_random_draws_match_oracles():
    rng = np.random.default_rng(20260825)
    for _ in range(8):
        n = int(rng.integers(3, 16))
        values = rng.uniform(0.0, 50.0, size=n)
        weights = rng.uniform(1.0, 20.0, size=n)
        rank = rng.uniform(0.0, 10.0, size=n)
        assert compute_gini(values, weights) == pytest.approx(
            gini_pairwise(values, weights), rel=1e-9, abs=1e-12
        )
        assert finite_or_equal(compute_palma_ratio(values, weights), palma_split_loop(values, weights))
        assert compute_concentration_index(
            values, rank, weights, rank_direction="higher_is_advantaged"
        ) == pytest.approx(
            concentration_index_grouped(values, rank, weights), rel=1e-9, abs=1e-12
        )
