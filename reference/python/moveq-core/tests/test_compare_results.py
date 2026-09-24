"""Difference intervals. Do not subtract two separate intervals."""

import numpy as np
import pytest

from moveq_core import compute_gini, gini_result

BASE_VALUES = np.array([1.0, 2.0, 4.0, 8.0])
BASE_WEIGHTS = np.array([10.0, 20.0, 30.0, 40.0])
PROP_VALUES = np.array([1.0, 3.0, 3.0, 9.0])
PROP_WEIGHTS = np.array([10.0, 20.0, 30.0, 40.0])
SEED = 11
N_BOOT = 40


def _paired_diff(n_boot, seed):
    rng = np.random.default_rng(seed)
    n = BASE_VALUES.size
    draws = rng.choice(n, size=(n_boot, n), replace=True)
    reps = np.empty(n_boot)
    for i in range(n_boot):
        reps[i] = compute_gini(PROP_VALUES[draws[i]], PROP_WEIGHTS[draws[i]]) - compute_gini(
            BASE_VALUES[draws[i]], BASE_WEIGHTS[draws[i]]
        )
    alpha = 0.025
    low, high = np.quantile(reps, [alpha, 1.0 - alpha], method="linear")
    return float(low), float(high)


def test_omitted_uncertainty_is_the_point_difference_only():
    from moveq_core import compare_results

    baseline = gini_result(BASE_VALUES, BASE_WEIGHTS)
    proposal = gini_result(PROP_VALUES, PROP_WEIGHTS)
    result = compare_results(baseline, proposal)
    assert result.difference == pytest.approx(proposal.value - baseline.value)
    assert result.ci_low is None
    assert result.ci_high is None
    assert result.n_boot is None


def test_paired_bootstrap_matches_shared_draws():
    from moveq_core import compare_results

    baseline = gini_result(BASE_VALUES, BASE_WEIGHTS)
    proposal = gini_result(PROP_VALUES, PROP_WEIGHTS)
    expected_low, expected_high = _paired_diff(N_BOOT, SEED)
    result = compare_results(
        baseline,
        proposal,
        uncertainty="bootstrap",
        n_boot=N_BOOT,
        seed=SEED,
        baseline_inputs=(BASE_VALUES, BASE_WEIGHTS),
        proposal_inputs=(PROP_VALUES, PROP_WEIGHTS),
    )
    assert result.difference == pytest.approx(proposal.value - baseline.value)
    assert result.ci_low == pytest.approx(expected_low)
    assert result.ci_high == pytest.approx(expected_high)
    assert result.parameters["paired"] is True
    assert result.parameters["seed"] == SEED
    text = " ".join(result.warnings) + " " + (result.note or "")
    assert "subtract" in text.lower()
