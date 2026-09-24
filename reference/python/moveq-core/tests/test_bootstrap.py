"""Bootstrap intervals are off unless the caller asks.

Oracle: nonparametric percentile bootstrap of areal units. Each draw keeps
the unit's population weight. The interval is NumPy's linear quantile of
the replicates (Hyndman–Fan type 7), matching statsmodels' pairs bootstrap
of independent observations — not a regression standard error.
"""

import numpy as np
import pytest

from moveq_core import (
    compute_concentration_index,
    compute_gini,
    compute_palma_ratio,
    concentration_index_result,
    gini_result,
    palma_result,
)

VALUES = np.array([1.0, 2.0, 4.0, 8.0])
WEIGHTS = np.array([10.0, 20.0, 30.0, 40.0])
RANK = np.array([1.0, 2.0, 3.0, 4.0])
SEED = 7
N_BOOT = 40
LEVEL = 0.95


def _replicates(statistic, columns, n_boot, seed):
    rng = np.random.default_rng(seed)
    n = columns[0].size
    draws = rng.choice(n, size=(n_boot, n), replace=True)
    reps = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        reps[i] = statistic(*(col[draws[i]] for col in columns))
    return reps


def _percentile(reps, level):
    alpha = (1.0 - level) / 2.0
    low, high = np.quantile(reps, [alpha, 1.0 - alpha], method="linear")
    return float(low), float(high)


def test_omitted_uncertainty_matches_point_estimate():
    plain = compute_gini(VALUES, WEIGHTS)
    result = gini_result(VALUES, WEIGHTS)
    assert result.value == plain
    assert result.ci_low is None
    assert result.ci_high is None
    assert result.uncertainty_method is None
    assert result.n_boot is None
    assert "seed" not in result.parameters
    assert "n_boot" not in result.parameters
    payload = result.to_dict()
    assert payload["ci_low"] is None
    assert payload["ci_high"] is None
    assert payload["uncertainty_method"] is None
    assert payload["n_boot"] is None


def test_gini_bootstrap_matches_percentile_oracle():
    expected_low, expected_high = _percentile(
        _replicates(compute_gini, (VALUES, WEIGHTS), N_BOOT, SEED), LEVEL
    )
    result = gini_result(
        VALUES, WEIGHTS, uncertainty="bootstrap", n_boot=N_BOOT, seed=SEED
    )
    assert result.value == compute_gini(VALUES, WEIGHTS)
    assert result.ci_low == pytest.approx(expected_low)
    assert result.ci_high == pytest.approx(expected_high)
    assert result.uncertainty_method == "bootstrap-percentile"
    assert result.n_boot == N_BOOT
    assert result.parameters["seed"] == SEED
    assert result.parameters["n_boot"] == N_BOOT
    assert result.parameters["uncertainty"] == "bootstrap"
    assert result.parameters["bootstrap_method"] == "percentile"
    assert result.parameters["resample"] == "areal-unit"
    assert result.ci_low <= result.value <= result.ci_high
    payload = result.to_dict()
    assert payload["ci_low"] == result.ci_low
    assert payload["n_boot"] == N_BOOT


def test_palma_and_ci_bootstrap_match_oracles():
    palma_low, palma_high = _percentile(
        _replicates(compute_palma_ratio, (VALUES, WEIGHTS), N_BOOT, SEED), LEVEL
    )
    palma = palma_result(
        VALUES, WEIGHTS, uncertainty="bootstrap", n_boot=N_BOOT, seed=SEED
    )
    assert palma.value == compute_palma_ratio(VALUES, WEIGHTS)
    assert palma.ci_low == pytest.approx(palma_low)
    assert palma.ci_high == pytest.approx(palma_high)

    def _ci(service, rank, population):
        return compute_concentration_index(
            service, rank, population, rank_direction="higher_is_advantaged"
        )

    ci_low, ci_high = _percentile(
        _replicates(_ci, (VALUES, RANK, WEIGHTS), N_BOOT, SEED), LEVEL
    )
    ci = concentration_index_result(
        VALUES,
        RANK,
        WEIGHTS,
        rank_direction="higher_is_advantaged",
        uncertainty="bootstrap",
        n_boot=N_BOOT,
        seed=SEED,
    )
    assert ci.value == _ci(VALUES, RANK, WEIGHTS)
    assert ci.ci_low == pytest.approx(ci_low)
    assert ci.ci_high == pytest.approx(ci_high)
    assert ci.parameters["seed"] == SEED
    assert ci.uncertainty_method == "bootstrap-percentile"


def test_bootstrap_is_deterministic_for_a_seed():
    kwargs = {"uncertainty": "bootstrap", "n_boot": N_BOOT, "seed": SEED}
    first = gini_result(VALUES, WEIGHTS, **kwargs)
    second = gini_result(VALUES, WEIGHTS, **kwargs)
    assert first.ci_low == second.ci_low
    assert first.ci_high == second.ci_high
    other = gini_result(VALUES, WEIGHTS, uncertainty="bootstrap", n_boot=N_BOOT, seed=SEED + 1)
    assert (other.ci_low, other.ci_high) != (first.ci_low, first.ci_high)
