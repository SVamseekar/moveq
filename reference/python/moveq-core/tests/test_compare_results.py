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
    payload = result.to_dict()
    assert payload["difference"] == result.difference
    assert payload["ci_low"] == result.ci_low


def test_rejects_mixed_metrics_and_a_bootstrap_without_inputs():
    from moveq_core import compare_results, palma_result

    baseline = gini_result(BASE_VALUES, BASE_WEIGHTS)
    proposal = palma_result(PROP_VALUES, PROP_WEIGHTS)
    with pytest.raises(ValueError, match="same metric"):
        compare_results(baseline, proposal)
    with pytest.raises(ValueError, match="baseline_inputs"):
        compare_results(baseline, baseline, uncertainty="bootstrap")


def test_undefined_point_skips_the_difference_interval():
    from moveq_core import compare_results, concentration_index_result

    service = np.array([0.0, 0.0, 0.0])
    rank = np.array([1.0, 2.0, 3.0])
    population = np.array([1.0, 1.0, 1.0])
    baseline = concentration_index_result(
        service, rank, population, rank_direction="higher_is_advantaged"
    )
    proposal = concentration_index_result(
        service, rank, population, rank_direction="higher_is_advantaged"
    )
    result = compare_results(
        baseline,
        proposal,
        uncertainty="bootstrap",
        n_boot=5,
        seed=SEED,
        baseline_inputs=(service, rank, population),
        proposal_inputs=(service, rank, population),
    )
    assert result.difference is None
    assert result.ci_low is None
    assert any("undefined" in warning for warning in result.warnings)


def test_unpaired_bootstrap_uses_separate_draws():
    from moveq_core import compare_results

    baseline = gini_result(BASE_VALUES, BASE_WEIGHTS)
    proposal = gini_result(PROP_VALUES[:3], PROP_WEIGHTS[:3])
    with pytest.raises(ValueError, match="same length"):
        compare_results(
            baseline,
            proposal,
            uncertainty="bootstrap",
            n_boot=N_BOOT,
            seed=SEED,
            baseline_inputs=(BASE_VALUES, BASE_WEIGHTS),
            proposal_inputs=(PROP_VALUES[:3], PROP_WEIGHTS[:3]),
        )
    result = compare_results(
        baseline,
        proposal,
        uncertainty="bootstrap",
        n_boot=N_BOOT,
        seed=SEED,
        paired=False,
        baseline_inputs=(BASE_VALUES, BASE_WEIGHTS),
        proposal_inputs=(PROP_VALUES[:3], PROP_WEIGHTS[:3]),
    )
    assert result.parameters["paired"] is False
    assert result.ci_low is not None and result.ci_high is not None
    assert result.note is not None and "subtract" in result.note.lower()


def test_palma_and_ci_differences_resample_their_estimators():
    from moveq_core import compare_results, concentration_index_result, palma_result

    base_palma = palma_result(BASE_VALUES, BASE_WEIGHTS)
    prop_palma = palma_result(PROP_VALUES, PROP_WEIGHTS)
    palma = compare_results(
        base_palma,
        prop_palma,
        uncertainty="bootstrap",
        n_boot=N_BOOT,
        seed=SEED,
        baseline_inputs=(BASE_VALUES, BASE_WEIGHTS),
        proposal_inputs=(PROP_VALUES, PROP_WEIGHTS),
    )
    assert palma.metric == "palma"
    assert palma.difference == pytest.approx(prop_palma.value - base_palma.value)
    assert palma.ci_low is not None

    rank = np.array([1.0, 2.0, 3.0, 4.0])
    base_ci = concentration_index_result(
        BASE_VALUES, rank, BASE_WEIGHTS, rank_direction="higher_is_advantaged"
    )
    prop_ci = concentration_index_result(
        PROP_VALUES, rank, PROP_WEIGHTS, rank_direction="higher_is_advantaged"
    )
    ci = compare_results(
        base_ci,
        prop_ci,
        uncertainty="bootstrap",
        n_boot=N_BOOT,
        seed=SEED,
        baseline_inputs=(BASE_VALUES, rank, BASE_WEIGHTS),
        proposal_inputs=(PROP_VALUES, rank, PROP_WEIGHTS),
    )
    assert ci.metric == "ci"
    assert ci.difference == pytest.approx(prop_ci.value - base_ci.value)
    assert ci.uncertainty_method == "bootstrap-percentile"
