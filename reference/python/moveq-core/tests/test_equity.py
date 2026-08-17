import numpy as np
import pytest

from moveq_core import compute_concentration_index, compute_gini, compute_palma_ratio


def test_gini_perfect_equality_is_zero():
    values = np.array([10.0, 10.0, 10.0, 10.0])
    weights = np.array([100.0, 100.0, 100.0, 100.0])
    assert compute_gini(values, weights) == pytest.approx(0.0, abs=1e-9)


def test_gini_extreme_inequality_approaches_one():
    # All service in one unit, none anywhere else.
    values = np.array([0.0, 0.0, 0.0, 100.0])
    weights = np.array([100.0, 100.0, 100.0, 100.0])
    gini = compute_gini(values, weights)
    assert 0.7 < gini < 1.0


def test_gini_is_order_invariant():
    values_a = np.array([5.0, 20.0, 1.0, 50.0])
    weights_a = np.array([900.0, 800.0, 1200.0, 300.0])
    order = [3, 1, 0, 2]
    gini_a = compute_gini(values_a, weights_a)
    gini_b = compute_gini(values_a[order], weights_a[order])
    assert gini_a == pytest.approx(gini_b, abs=1e-9)


def test_palma_ratio_equal_service_is_one():
    values = np.array([10.0] * 10)
    weights = np.array([100.0] * 10)
    assert compute_palma_ratio(values, weights) == pytest.approx(1.0, abs=1e-9)


def test_palma_ratio_top_heavy_is_greater_than_one():
    values = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 100.0])
    weights = np.array([100.0] * 10)
    assert compute_palma_ratio(values, weights) > 1.0


def test_concentration_index_pro_rich_when_service_rises_with_rank():
    service = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    rank = np.array([1, 2, 3, 4, 5])  # higher rank = less deprived
    population = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
    ci = compute_concentration_index(service, rank, population)
    assert ci > 0


def test_concentration_index_pro_poor_when_service_falls_with_rank():
    service = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
    rank = np.array([1, 2, 3, 4, 5])
    population = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
    ci = compute_concentration_index(service, rank, population)
    assert ci < 0


def test_concentration_index_flat_service_is_zero():
    service = np.array([3.0, 3.0, 3.0, 3.0, 3.0])
    rank = np.array([1, 2, 3, 4, 5])
    population = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
    ci = compute_concentration_index(service, rank, population)
    assert ci == pytest.approx(0.0, abs=1e-9)
