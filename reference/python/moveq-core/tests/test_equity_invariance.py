"""Documented invariance properties of Gini, Palma, and the Concentration Index."""

import numpy as np
import pytest

from moveq_core import compute_concentration_index, compute_gini, compute_palma_ratio

from oracles import finite_or_equal


def _shuffled_together(rng, *arrays):
    n = arrays[0].size
    order = rng.permutation(n)
    return tuple(a[order] for a in arrays)


def test_gini_is_invariant_to_positive_value_scale():
    values = np.array([5.0, 20.0, 1.0, 50.0])
    weights = np.array([900.0, 800.0, 1200.0, 300.0])
    base = compute_gini(values, weights)
    assert compute_gini(3.7 * values, weights) == pytest.approx(base, abs=1e-12)


def test_gini_is_invariant_to_positive_weight_scale():
    values = np.array([5.0, 20.0, 1.0, 50.0])
    weights = np.array([900.0, 800.0, 1200.0, 300.0])
    base = compute_gini(values, weights)
    assert compute_gini(values, 11.0 * weights) == pytest.approx(base, abs=1e-12)


def test_gini_is_permutation_invariant():
    rng = np.random.default_rng(1)
    values = np.array([5.0, 20.0, 1.0, 50.0, 8.0])
    weights = np.array([900.0, 800.0, 1200.0, 300.0, 50.0])
    base = compute_gini(values, weights)
    shuffled_v, shuffled_w = _shuffled_together(rng, values, weights)
    assert compute_gini(shuffled_v, shuffled_w) == pytest.approx(base, abs=1e-12)


def test_gini_non_negative_and_at_most_one():
    rng = np.random.default_rng(2)
    for _ in range(12):
        n = int(rng.integers(1, 12))
        values = rng.uniform(0.0, 80.0, size=n)
        weights = rng.uniform(0.1, 30.0, size=n)
        g = compute_gini(values, weights)
        assert 0.0 <= g <= 1.0 + 1e-12


def test_gini_zero_iff_equal_service():
    weights = np.array([12.0, 3.0, 40.0, 7.0])
    assert compute_gini(np.full(4, 6.5), weights) == pytest.approx(0.0, abs=1e-12)
    assert compute_gini(np.array([6.5, 6.5, 6.6, 6.5]), weights) > 0.0


def test_palma_is_invariant_to_positive_value_scale():
    values = np.array([1.0, 2.0, 10.0, 100.0])
    weights = np.array([40.0, 40.0, 15.0, 5.0])
    base = compute_palma_ratio(values, weights)
    assert compute_palma_ratio(4.0 * values, weights) == pytest.approx(base, rel=1e-12)


def test_palma_is_invariant_to_positive_weight_scale():
    values = np.array([1.0, 2.0, 10.0, 100.0])
    weights = np.array([40.0, 40.0, 15.0, 5.0])
    base = compute_palma_ratio(values, weights)
    assert compute_palma_ratio(values, 2.5 * weights) == pytest.approx(base, rel=1e-12)


def test_palma_is_permutation_invariant():
    rng = np.random.default_rng(3)
    values = np.array([1.0, 2.0, 10.0, 100.0, 3.0])
    weights = np.array([40.0, 40.0, 15.0, 5.0, 8.0])
    base = compute_palma_ratio(values, weights)
    shuffled_v, shuffled_w = _shuffled_together(rng, values, weights)
    assert finite_or_equal(compute_palma_ratio(shuffled_v, shuffled_w), base)


def test_palma_at_least_one_for_non_negative_service():
    rng = np.random.default_rng(4)
    for _ in range(12):
        n = int(rng.integers(2, 12))
        values = rng.uniform(0.0, 80.0, size=n)
        weights = rng.uniform(0.1, 30.0, size=n)
        p = compute_palma_ratio(values, weights)
        assert p >= 1.0 or p == float("inf")


def test_palma_population_weighting_matters():
    # Three units: shifting mass onto the richest area pulls that area into
    # the bottom 40% split, so the ratio must change.
    values = np.array([1.0, 2.0, 10.0])
    balanced = compute_palma_ratio(values, np.array([40.0, 50.0, 10.0]))
    skewed = compute_palma_ratio(values, np.array([10.0, 10.0, 80.0]))
    assert balanced != pytest.approx(skewed, rel=1e-9)


def test_concentration_index_is_invariant_to_positive_service_scale():
    service = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    rank = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    population = np.array([100.0, 80.0, 60.0, 40.0, 20.0])
    base = compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged")
    assert compute_concentration_index(
        2.0 * service, rank, population, rank_direction="higher_is_advantaged"
    ) == pytest.approx(base, abs=1e-12)


def test_concentration_index_is_invariant_to_positive_population_scale():
    service = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    rank = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    population = np.array([100.0, 80.0, 60.0, 40.0, 20.0])
    base = compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged")
    assert compute_concentration_index(
        service, rank, 3.0 * population, rank_direction="higher_is_advantaged"
    ) == pytest.approx(base, abs=1e-12)


def test_concentration_index_is_permutation_invariant():
    rng = np.random.default_rng(5)
    service = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    rank = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    population = np.array([100.0, 80.0, 60.0, 40.0, 20.0])
    base = compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged")
    shuffled = _shuffled_together(rng, service, rank, population)
    assert compute_concentration_index(
        *shuffled, rank_direction="higher_is_advantaged"
    ) == pytest.approx(base, abs=1e-12)


def test_concentration_index_rank_reversal_negates():
    service = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    rank = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    population = np.array([100.0, 80.0, 60.0, 40.0, 20.0])
    base = compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged")
    reversed_rank = -rank
    assert compute_concentration_index(
        service, reversed_rank, population, rank_direction="higher_is_advantaged"
    ) == pytest.approx(
        -base, abs=1e-12
    )


def test_concentration_index_constant_service_is_zero():
    service = np.array([4.0, 4.0, 4.0, 4.0])
    rank = np.array([1.0, 8.0, 3.0, 2.0])
    population = np.array([10.0, 40.0, 5.0, 20.0])
    assert compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged") == pytest.approx(0.0, abs=1e-12)


def test_concentration_index_in_unit_interval_for_non_negative_service():
    rng = np.random.default_rng(6)
    for _ in range(12):
        n = int(rng.integers(2, 12))
        service = rng.uniform(0.0, 80.0, size=n)
        rank = rng.uniform(0.0, 10.0, size=n)
        population = rng.uniform(0.1, 30.0, size=n)
        ci = compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged")
        assert -1.0 - 1e-12 <= ci <= 1.0 + 1e-12
