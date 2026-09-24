"""Cluster bootstrap resamples groups, not areal units. Off unless asked."""

import numpy as np
import pytest

from moveq_core import compute_gini, gini_result

VALUES = np.array([1.0, 1.0, 5.0, 9.0, 9.0, 9.0])
WEIGHTS = np.array([10.0, 10.0, 10.0, 10.0, 10.0, 10.0])
CLUSTER = np.array(["north", "north", "north", "south", "south", "south"])
SEED = 3
N_BOOT = 30


def _cluster_percentile(values, weights, cluster, n_boot, seed, level=0.95):
    codes, inverse = np.unique(cluster, return_inverse=True)
    groups = [np.flatnonzero(inverse == i) for i in range(codes.size)]
    rng = np.random.default_rng(seed)
    chosen = rng.choice(codes.size, size=(n_boot, codes.size), replace=True)
    reps = np.empty(n_boot)
    for b in range(n_boot):
        idx = np.concatenate([groups[i] for i in chosen[b]])
        reps[b] = compute_gini(values[idx], weights[idx])
    alpha = (1.0 - level) / 2.0
    low, high = np.quantile(reps, [alpha, 1.0 - alpha], method="linear")
    return float(low), float(high)


def test_cluster_bootstrap_matches_oracle_and_records_definition():
    expected_low, expected_high = _cluster_percentile(
        VALUES, WEIGHTS, CLUSTER, N_BOOT, SEED
    )
    result = gini_result(
        VALUES,
        WEIGHTS,
        uncertainty="bootstrap",
        cluster=CLUSTER,
        n_boot=N_BOOT,
        seed=SEED,
    )
    assert result.value == compute_gini(VALUES, WEIGHTS)
    assert result.ci_low == pytest.approx(expected_low)
    assert result.ci_high == pytest.approx(expected_high)
    assert result.parameters["resample"] == "cluster"
    assert result.parameters["n_clusters"] == 2
    assert result.parameters["cluster_labels"] == ["north", "south"]
    assert result.parameters["seed"] == SEED


def test_omitted_cluster_stays_areal_unit_bootstrap():
    unit = gini_result(VALUES, WEIGHTS, uncertainty="bootstrap", n_boot=N_BOOT, seed=SEED)
    assert unit.parameters["resample"] == "areal-unit"
    clustered = gini_result(
        VALUES,
        WEIGHTS,
        uncertainty="bootstrap",
        cluster=CLUSTER,
        n_boot=N_BOOT,
        seed=SEED,
    )
    assert (clustered.ci_low, clustered.ci_high) != (unit.ci_low, unit.ci_high)


def test_cluster_without_bootstrap_is_rejected():
    with pytest.raises(ValueError, match="cluster"):
        gini_result(VALUES, WEIGHTS, cluster=CLUSTER)
