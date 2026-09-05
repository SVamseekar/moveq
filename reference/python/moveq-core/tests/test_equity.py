import numpy as np
import pytest

from moveq_core import compute_concentration_index, compute_gini, compute_palma_ratio


def test_gini_zero_total_service_is_zero_by_convention():
    values = np.array([0.0, 0.0, 0.0, 0.0])
    weights = np.array([100.0, 100.0, 100.0, 100.0])
    assert compute_gini(values, weights) == pytest.approx(0.0, abs=1e-9)


def test_gini_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        compute_gini(np.array([1.0, 2.0]), np.array([1.0, 2.0, 3.0]))


def test_gini_allows_individual_zero_weight():
    # A single unpopulated area (weight=0) contributes nothing and should
    # not be rejected — only a negative weight or an all-zero total is invalid.
    with_zero = compute_gini(np.array([1.0, 2.0, 5.0]), np.array([1.0, 0.0, 3.0]))
    without_zero = compute_gini(np.array([1.0, 5.0]), np.array([1.0, 3.0]))
    assert with_zero == pytest.approx(without_zero, abs=1e-9)


def test_gini_rejects_negative_weight():
    with pytest.raises(ValueError):
        compute_gini(np.array([1.0, 2.0]), np.array([1.0, -1.0]))


def test_gini_rejects_all_zero_weights():
    with pytest.raises(ValueError):
        compute_gini(np.array([1.0, 2.0]), np.array([0.0, 0.0]))


def test_gini_rejects_negative_values():
    with pytest.raises(ValueError):
        compute_gini(np.array([-1.0, 2.0]), np.array([1.0, 1.0]))


def test_gini_rejects_non_finite_input():
    with pytest.raises(ValueError):
        compute_gini(np.array([1.0, np.nan]), np.array([1.0, 1.0]))


def test_gini_perfect_equality_is_zero():
    values = np.array([10.0, 10.0, 10.0, 10.0])
    weights = np.array([100.0, 100.0, 100.0, 100.0])
    assert compute_gini(values, weights) == pytest.approx(0.0, abs=1e-9)


def test_gini_two_units_one_has_all_is_one_half():
    # Equal-weight two-person Lorenz: (0,0) → (0.5,0) → (1,1). Area 0.25, Gini 0.5.
    values = np.array([0.0, 1.0])
    weights = np.array([1.0, 1.0])
    assert compute_gini(values, weights) == pytest.approx(0.5, abs=1e-12)


def test_gini_extreme_inequality_is_one_minus_one_over_n():
    # Equal weights, all service in one of n units: G = (n - 1) / n.
    values = np.array([0.0, 0.0, 0.0, 100.0])
    weights = np.array([100.0, 100.0, 100.0, 100.0])
    assert compute_gini(values, weights) == pytest.approx(0.75, abs=1e-12)


def test_gini_rejects_2d_arrays():
    values = np.array([[1.0, 2.0], [3.0, 4.0]])
    weights = np.array([[1.0, 1.0], [1.0, 1.0]])
    with pytest.raises(ValueError, match="1-dimensional"):
        compute_gini(values, weights)


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


def test_palma_ratio_splits_boundary_area_proportionally():
    # One big area (60% of pop) straddles the bottom-40% cut. A whole-unit
    # truncation would drop it from "bottom" entirely; the correct answer
    # counts the 40% of its population that falls below the cut.
    values = np.array([1.0, 10.0, 2.0, 2.0])
    weights = np.array([30.0, 10.0, 30.0, 30.0])
    # sorted by value: [1.0 (30), 2.0 (30), 2.0 (30), 10.0 (10)], total=100
    # bottom 40 population units: all of the first area (30) + 10 of the second (2.0)
    # bottom_mean = (1.0*30 + 2.0*10) / 40 = 50/40 = 1.25
    assert compute_palma_ratio(values, weights) == pytest.approx(10.0 / 1.25, rel=1e-9)


def test_palma_ratio_is_order_invariant_for_tied_values():
    values = np.array([1.0, 1.0, 5.0, 5.0])
    weights = np.array([20.0, 40.0, 20.0, 20.0])
    order = [1, 0, 3, 2]
    palma_a = compute_palma_ratio(values, weights)
    palma_b = compute_palma_ratio(values[order], weights[order])
    assert palma_a == pytest.approx(palma_b, abs=1e-9)


def test_palma_ratio_splits_top_boundary_area_proportionally():
    # Third area (weight 15) straddles the 90% cut; only 5 of its 15 people
    # belong in the top 10%, plus the whole last area.
    values = np.array([1.0, 2.0, 10.0, 100.0])
    weights = np.array([40.0, 40.0, 15.0, 5.0])
    # bottom 40: first area only, mean = 1.0
    # top 10: 5 people at 10 + 5 people at 100, mean = 55
    assert compute_palma_ratio(values, weights) == pytest.approx(55.0, rel=1e-9)


def test_palma_ratio_zero_service_is_one_by_convention():
    values = np.array([0.0, 0.0, 0.0, 0.0])
    weights = np.array([100.0, 100.0, 100.0, 100.0])
    assert compute_palma_ratio(values, weights) == pytest.approx(1.0, abs=1e-12)


def test_palma_ratio_bottom_zero_top_positive_is_inf():
    values = np.array([0.0, 0.0, 0.0, 0.0, 10.0])
    weights = np.array([40.0, 20.0, 20.0, 10.0, 10.0])
    assert compute_palma_ratio(values, weights) == float("inf")


def test_palma_ratio_rejects_2d_arrays():
    with pytest.raises(ValueError, match="1-dimensional"):
        compute_palma_ratio(np.ones((2, 2)), np.ones((2, 2)))


def test_concentration_index_advantage_concentrated_when_service_rises_with_rank():
    service = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    rank = np.array([1, 2, 3, 4, 5])  # higher rank = less deprived
    population = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
    ci = compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged")
    assert ci > 0


def test_concentration_index_disadvantage_concentrated_when_service_falls_with_rank():
    service = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
    rank = np.array([1, 2, 3, 4, 5])
    population = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
    ci = compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged")
    assert ci < 0


def test_concentration_index_flat_service_is_zero():
    service = np.array([3.0, 3.0, 3.0, 3.0, 3.0])
    rank = np.array([1, 2, 3, 4, 5])
    population = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
    ci = compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged")
    assert ci == pytest.approx(0.0, abs=1e-9)


def test_concentration_index_is_order_invariant_for_tied_ranks():
    # Two areas tie on rank=1 with different service and population, so a
    # naive argsort's arbitrary tie-break would assign different fractional
    # ranks to them depending on input order.
    service = np.array([10.0, 2.0, 5.0])
    rank = np.array([1, 1, 2])
    population = np.array([50.0, 150.0, 200.0])
    order = [1, 0, 2]
    ci_a = compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged")
    ci_b = compute_concentration_index(
        service[order], rank[order], population[order], rank_direction="higher_is_advantaged"
    )
    assert ci_a == pytest.approx(ci_b, abs=1e-9)


def test_concentration_index_equal_weight_known_value():
    # n=5, equal population, y = 1..5, R_i = (i - 0.5)/5.
    # cov_w(y, R) = 0.4, μ = 3, CI = 2 * 0.4 / 3.
    service = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    rank = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    population = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
    assert compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged") == pytest.approx(0.8 / 3.0, abs=1e-12)


def test_concentration_index_tied_ranks_use_group_midpoint():
    # Rank-1 group occupies the first 200 of 400 people, so both units share
    # R = 0.25. The remaining unit has R = 0.75.
    service = np.array([10.0, 2.0, 5.0])
    rank = np.array([1.0, 1.0, 2.0])
    population = np.array([50.0, 150.0, 200.0])
    mu = (10.0 * 50 + 2.0 * 150 + 5.0 * 200) / 400.0
    r = np.array([0.25, 0.25, 0.75])
    cov = float(np.sum(population * (service - mu) * (r - 0.5)) / 400.0)
    expected = 2.0 * cov / mu
    assert compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged") == pytest.approx(expected, abs=1e-12)


def test_concentration_index_zero_population_unit_is_ignored():
    service = np.array([1.0, 99.0, 5.0])
    rank = np.array([1.0, 99.0, 2.0])
    population = np.array([100.0, 0.0, 100.0])
    without = compute_concentration_index(
        np.array([1.0, 5.0]),
        np.array([1.0, 2.0]),
        np.array([100.0, 100.0]),
        rank_direction="higher_is_advantaged",
    )
    with_zero = compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged")
    assert with_zero == pytest.approx(without, abs=1e-12)


def test_concentration_index_zero_mean_service_is_undefined():
    from moveq_core import UndefinedMetricError

    service = np.array([0.0, 0.0, 0.0])
    rank = np.array([1.0, 2.0, 3.0])
    population = np.array([10.0, 10.0, 10.0])
    with pytest.raises(UndefinedMetricError, match="zero_mean"):
        compute_concentration_index(
            service, rank, population, rank_direction="higher_is_advantaged"
        )


def test_concentration_index_negative_mean_service_is_defined():
    # Same gradient as the known-value case, shifted to a negative mean.
    # cov_w = 0.4, μ = -3, CI = 2 * 0.4 / -3.
    service = np.array([-5.0, -4.0, -3.0, -2.0, -1.0])
    rank = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    population = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
    assert compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged") == pytest.approx(-0.8 / 3.0, abs=1e-12)


def test_concentration_index_rejects_2d_arrays():
    service = np.ones((2, 2))
    rank = np.ones((2, 2))
    population = np.ones((2, 2))
    with pytest.raises(ValueError, match="1-dimensional"):
        compute_concentration_index(service, rank, population, rank_direction="higher_is_advantaged")


def test_concentration_index_rejects_mismatched_rank_length():
    with pytest.raises(ValueError, match="same length"):
        compute_concentration_index(
            np.array([1.0, 2.0]),
            np.array([1.0]),
            np.array([1.0, 1.0]),
            rank_direction="higher_is_advantaged",
        )
