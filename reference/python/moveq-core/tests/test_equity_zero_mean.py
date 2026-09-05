"""Zero and near-zero mean make the relative Concentration Index undefined."""

from __future__ import annotations

import json
import warnings

import numpy as np
import pytest

from moveq_core import (
    UndefinedMetricError,
    compute_concentration_index,
    concentration_index_result,
)

_ADV = "higher_is_advantaged"


def test_all_zero_service_is_structured_undefined():
    service = np.array([0.0, 0.0, 0.0])
    rank = np.array([1.0, 2.0, 3.0])
    population = np.array([10.0, 20.0, 30.0])
    result = concentration_index_result(
        service, rank, population, rank_direction=_ADV
    )
    assert result.value is None
    assert result.status == "undefined"
    assert result.reason == "zero_mean"
    assert result.warnings
    assert result.n_areas == 3
    assert result.n_dropped == 0
    assert result.total_population == pytest.approx(60.0)
    assert result.method == "wagstaff-covariance"
    assert result.context == {}


def test_scalar_api_raises_undefined_with_result():
    service = np.array([0.0, 0.0, 0.0])
    rank = np.array([1.0, 2.0, 3.0])
    population = np.array([10.0, 10.0, 10.0])
    with pytest.raises(UndefinedMetricError) as excinfo:
        compute_concentration_index(service, rank, population, rank_direction=_ADV)
    err = excinfo.value
    assert err.metric == "ci"
    assert err.reason == "zero_mean"
    assert err.result.value is None
    assert err.result.n_areas == 3
    assert err.result.total_population == pytest.approx(30.0)


def test_cancellation_is_near_zero_mean():
    service = np.array([100.0, -100.0])
    rank = np.array([1.0, 2.0])
    population = np.array([1.0, 1.0])
    result = concentration_index_result(
        service, rank, population, rank_direction=_ADV
    )
    assert result.status == "undefined"
    assert result.reason == "near_zero_mean"
    assert result.value is None


def test_cancellation_is_scale_free():
    rank = np.array([1.0, 2.0])
    population = np.array([1.0, 1.0])
    for scale in (1.0, 1e6):
        service = np.array([100.0, -100.0]) * scale
        result = concentration_index_result(
            service, rank, population, rank_direction=_ADV
        )
        assert result.status == "undefined", scale
        assert result.reason == "near_zero_mean", scale


def test_just_above_threshold_is_defined():
    # Cancellation ratio well above 1e-9.
    service = np.array([1.0, -0.5])
    rank = np.array([1.0, 2.0])
    population = np.array([1.0, 1.0])
    result = concentration_index_result(
        service, rank, population, rank_direction=_ADV
    )
    assert result.status == "ok"
    assert result.value is not None
    assert np.isfinite(result.value)
    assert result.reason is None


def test_legacy_zero_returns_zero_and_warns():
    service = np.array([0.0, 0.0])
    rank = np.array([1.0, 2.0])
    population = np.array([1.0, 1.0])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = concentration_index_result(
            service,
            rank,
            population,
            rank_direction=_ADV,
            zero_mean="legacy_zero",
        )
        scalar = compute_concentration_index(
            service,
            rank,
            population,
            rank_direction=_ADV,
            zero_mean="legacy_zero",
        )
    assert result.value == pytest.approx(0.0)
    assert result.status == "ok"
    assert scalar == pytest.approx(0.0)
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_to_dict_serialises_undefined_value_as_null():
    service = np.array([0.0, 0.0])
    rank = np.array([1.0, 2.0])
    population = np.array([1.0, 1.0])
    data = concentration_index_result(
        service, rank, population, rank_direction=_ADV
    ).to_dict()
    assert data["value"] is None
    assert data["status"] == "undefined"
    assert data["reason"] == "zero_mean"
    encoded = json.dumps(data)
    assert '"value": null' in encoded
    assert json.loads(encoded)["value"] is None
