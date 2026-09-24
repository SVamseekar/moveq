"""Small-sample warnings. Thresholds are recorded, not silent."""

import numpy as np

from moveq_core import concentration_index_result, gini_result, palma_result


def test_palma_warns_at_household_scale_and_not_at_3000():
    household = palma_result(np.arange(1.0, 6.0), np.ones(5))
    assert any("Palma" in warning and "few units" in warning for warning in household.warnings)
    assert household.parameters["palma_min_units_in_tail"] == 5

    large = palma_result(np.linspace(1.0, 2.0, 3000), np.ones(3000))
    assert not any("few units" in warning for warning in large.warnings)
    assert large.parameters["palma_min_units_in_tail"] == 5


def test_small_effective_sample_warns():
    result = gini_result(np.array([1.0, 2.0, 3.0]), np.ones(3))
    assert any("effective sample size" in warning for warning in result.warnings)
    assert result.parameters["small_n_areas"] == 30
    assert result.value == gini_result(np.array([1.0, 2.0, 3.0]), np.ones(3)).value


def test_thin_rank_group_warns():
    result = concentration_index_result(
        np.array([1.0, 2.0, 3.0]),
        np.array([1.0, 1.0, 2.0]),
        np.array([100.0, 100.0, 1.0]),
        rank_direction="higher_is_advantaged",
    )
    assert any("rank group" in warning for warning in result.warnings)
    assert result.parameters["rank_group_min_share"] == 0.05


def test_bootstrap_half_gap_warns_when_the_halves_disagree():
    result = gini_result(
        np.array([1.0, 2.0, 3.0, 50.0]),
        np.ones(4),
        uncertainty="bootstrap",
        n_boot=20,
        seed=3,
    )
    assert any("unstable" in warning for warning in result.warnings)


def test_equal_bootstrap_is_not_flagged_unstable():
    result = gini_result(
        np.ones(40),
        np.ones(40),
        uncertainty="bootstrap",
        n_boot=40,
        seed=1,
    )
    assert not any("unstable" in warning for warning in result.warnings)
    assert result.parameters["bootstrap_half_gap"] == 0.05
