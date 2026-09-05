"""Input-shape and documented-convention cases for the equity metrics."""

import numpy as np
import pytest

from moveq_core import compute_concentration_index, compute_gini, compute_palma_ratio


def test_gini_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        compute_gini(np.array([]), np.array([]))


def test_palma_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        compute_palma_ratio(np.array([]), np.array([]))


def test_concentration_index_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        compute_concentration_index(
            np.array([]), np.array([]), np.array([]), rank_direction="higher_is_advantaged"
        )


def test_gini_single_observation_is_zero():
    assert compute_gini(np.array([7.5]), np.array([120.0])) == pytest.approx(0.0, abs=1e-12)


def test_palma_single_observation_is_one():
    # The one unit is split across both tails, so the means are equal.
    assert compute_palma_ratio(np.array([7.5]), np.array([120.0])) == pytest.approx(1.0, abs=1e-12)


def test_concentration_index_single_observation_is_zero():
    assert compute_concentration_index(
        np.array([7.5]), np.array([3.0]), np.array([120.0]), rank_direction="higher_is_advantaged"
    ) == pytest.approx(0.0, abs=1e-12)


def test_gini_rejects_inf_values():
    with pytest.raises(ValueError, match="finite"):
        compute_gini(np.array([1.0, np.inf]), np.array([1.0, 1.0]))


def test_gini_rejects_inf_weights():
    with pytest.raises(ValueError, match="finite"):
        compute_gini(np.array([1.0, 2.0]), np.array([1.0, np.inf]))


def test_palma_rejects_nan_weights():
    with pytest.raises(ValueError, match="finite"):
        compute_palma_ratio(np.array([1.0, 2.0]), np.array([1.0, np.nan]))


def test_concentration_index_rejects_nan_rank():
    with pytest.raises(ValueError, match="finite"):
        compute_concentration_index(
            np.array([1.0, 2.0]),
            np.array([1.0, np.nan]),
            np.array([1.0, 1.0]),
            rank_direction="higher_is_advantaged",
        )


def test_palma_zero_weight_unit_is_ignored():
    with_zero = compute_palma_ratio(np.array([1.0, 99.0, 5.0]), np.array([40.0, 0.0, 60.0]))
    without = compute_palma_ratio(np.array([1.0, 5.0]), np.array([40.0, 60.0]))
    assert with_zero == pytest.approx(without, abs=1e-12)


def test_palma_rejects_negative_values():
    with pytest.raises(ValueError):
        compute_palma_ratio(np.array([-1.0, 2.0]), np.array([1.0, 1.0]))


def test_palma_rejects_all_zero_weights():
    with pytest.raises(ValueError):
        compute_palma_ratio(np.array([1.0, 2.0]), np.array([0.0, 0.0]))


def test_concentration_index_rejects_all_zero_population():
    with pytest.raises(ValueError):
        compute_concentration_index(
            np.array([1.0, 2.0]),
            np.array([1.0, 2.0]),
            np.array([0.0, 0.0]),
            rank_direction="higher_is_advantaged",
        )
