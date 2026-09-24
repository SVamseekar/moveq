"""Bootstrap intervals are off unless the caller asks.

Oracle: nonparametric percentile bootstrap of areal units. Each draw keeps
the unit's population weight. The interval is NumPy's linear quantile of
the replicates (Hyndman–Fan type 7), matching statsmodels' pairs bootstrap
of independent observations — not a regression standard error.
"""

import math

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


def test_palma_percentile_keeps_infinite_replicates():
    values = np.array([0.0, 0.0, 0.0, 0.0, 10.0])
    weights = np.array([40.0, 20.0, 20.0, 10.0, 10.0])
    result = palma_result(values, weights, uncertainty="bootstrap", n_boot=20, seed=1)
    assert math.isinf(result.value)
    assert result.ci_high is not None and math.isinf(result.ci_high)
    assert not any("undefined" in warning for warning in result.warnings)


def test_legacy_zero_mean_does_not_bootstrap_around_convention_zero():
    service = np.array([0.0, 0.0, 0.0])
    rank = np.array([1.0, 2.0, 3.0])
    population = np.array([10.0, 10.0, 10.0])
    result = concentration_index_result(
        service,
        rank,
        population,
        rank_direction="higher_is_advantaged",
        zero_mean="legacy_zero",
        uncertainty="bootstrap",
        n_boot=20,
        seed=1,
    )
    assert result.value == 0.0
    assert result.ci_low is None
    assert result.ci_high is None


def test_bootstrap_is_deterministic_for_a_seed():
    kwargs = {"uncertainty": "bootstrap", "n_boot": N_BOOT, "seed": SEED}
    first = gini_result(VALUES, WEIGHTS, **kwargs)
    second = gini_result(VALUES, WEIGHTS, **kwargs)
    assert first.ci_low == second.ci_low
    assert first.ci_high == second.ci_high
    other = gini_result(VALUES, WEIGHTS, uncertainty="bootstrap", n_boot=N_BOOT, seed=SEED + 1)
    assert (other.ci_low, other.ci_high) != (first.ci_low, first.ci_high)


def test_bootstrap_rejects_bad_uncertainty_count_and_level():
    with pytest.raises(ValueError, match="uncertainty must be"):
        gini_result(VALUES, WEIGHTS, uncertainty="analytic")
    with pytest.raises(ValueError, match="n_boot"):
        gini_result(VALUES, WEIGHTS, uncertainty="bootstrap", n_boot=0, seed=SEED)
    with pytest.raises(ValueError, match="n_boot"):
        gini_result(VALUES, WEIGHTS, uncertainty="bootstrap", n_boot=True, seed=SEED)
    with pytest.raises(ValueError, match="level"):
        gini_result(
            VALUES, WEIGHTS, uncertainty="bootstrap", n_boot=N_BOOT, seed=SEED, level=0.0
        )
    with pytest.raises(ValueError, match="level"):
        gini_result(
            VALUES, WEIGHTS, uncertainty="bootstrap", n_boot=N_BOOT, seed=SEED, level=1.0
        )


def test_omitted_seed_is_drawn_and_recorded():
    result = gini_result(VALUES, WEIGHTS, uncertainty="bootstrap", n_boot=5, seed=None)
    assert isinstance(result.parameters["seed"], int)
    assert result.n_boot == 5
    assert result.ci_low is not None


def test_single_replicate_interval_equals_that_draw():
    expected = _replicates(compute_gini, (VALUES, WEIGHTS), 1, SEED)[0]
    result = gini_result(VALUES, WEIGHTS, uncertainty="bootstrap", n_boot=1, seed=SEED)
    assert result.ci_low == pytest.approx(expected)
    assert result.ci_high == pytest.approx(expected)


def test_linear_quantile_returns_nonfinite_left_neighbour():
    from moveq_core.equity import _linear_quantile

    # Sorted left is -inf and right is finite, so the interval must not interpolate.
    assert _linear_quantile(np.array([-np.inf, 1.0]), 0.5) == -np.inf


def test_undefined_replicates_omit_the_interval():
    service = np.array([0.0, 0.0, 4.0])
    rank = np.array([1.0, 2.0, 3.0])
    population = np.array([1.0, 1.0, 1.0])
    found = None
    for seed in range(40):
        result = concentration_index_result(
            service,
            rank,
            population,
            rank_direction="higher_is_advantaged",
            uncertainty="bootstrap",
            n_boot=1,
            seed=seed,
        )
        if result.ci_low is None and result.value is not None:
            found = result
            break
    assert found is not None
    assert any("no interval is reported" in warning for warning in found.warnings)


def test_generalized_bootstrap_skips_undefined_draws():
    service = np.array([0.0, 0.0, 1.0])
    rank = np.array([1.0, 2.0, 3.0])
    population = np.array([1.0, 1.0, 1.0])
    seed = None
    for candidate in range(40):
        draws = np.random.default_rng(candidate).choice(3, size=(12, 3), replace=True)
        rows = service[draws]
        all_zero = np.all(rows == 0.0, axis=1)
        if all_zero.any() and (~all_zero).any():
            seed = candidate
            break
    assert seed is not None
    result = concentration_index_result(
        service,
        rank,
        population,
        rank_direction="higher_is_advantaged",
        variant="generalized",
        uncertainty="bootstrap",
        n_boot=12,
        seed=seed,
    )
    assert result.value is not None
    assert result.uncertainty_method == "bootstrap-percentile"
    assert result.ci_low is not None and result.ci_high is not None


def test_software_version_falls_back_when_metadata_is_missing(monkeypatch):
    from moveq_core import __version__
    from moveq_core.equity import _software_version

    def missing(_name):
        raise ModuleNotFoundError("moveq-core")

    monkeypatch.setattr("importlib.metadata.version", missing)
    assert _software_version() == __version__


def test_numpy_without_an_integrator_is_rejected():
    import importlib

    import numpy as np

    import moveq_core.equity as equity

    snapshot = dict(equity.__dict__)
    removed = {}
    for name in ("trapezoid", "trapz"):
        if hasattr(np, name):
            removed[name] = getattr(np, name)
            delattr(np, name)
    try:
        with pytest.raises(ImportError, match="trapezoid"):
            importlib.reload(equity)
    finally:
        for name, fn in removed.items():
            setattr(np, name, fn)
        equity.__dict__.clear()
        equity.__dict__.update(snapshot)
