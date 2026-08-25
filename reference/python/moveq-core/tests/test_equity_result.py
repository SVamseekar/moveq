"""Auditable EquityResult objects wrapping Gini, Palma, and CI."""

import math

import numpy as np
import pytest

from moveq_core import (
    EquityResult,
    compute_concentration_index,
    compute_gini,
    compute_palma_ratio,
    concentration_index_result,
    gini_result,
    palma_result,
)

EQUAL_SERVICE = np.array([10.0, 10.0, 10.0, 10.0])
EQUAL_WEIGHTS = np.array([100.0, 100.0, 100.0, 100.0])
ZERO_SERVICE = np.array([0.0, 0.0, 0.0, 0.0])
UNEVEN_SERVICE = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
UNEVEN_WEIGHTS = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
UNEVEN_RANK = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

TO_DICT_KEYS = {
    "metric",
    "value",
    "method",
    "n_areas",
    "n_dropped",
    "total_population",
    "parameters",
    "warnings",
    "note",
    "context",
}


def test_gini_result_value_matches_compute_gini():
    result = gini_result(UNEVEN_SERVICE, UNEVEN_WEIGHTS)
    assert result.value == compute_gini(UNEVEN_SERVICE, UNEVEN_WEIGHTS)


def test_palma_result_value_matches_compute_palma():
    result = palma_result(UNEVEN_SERVICE, UNEVEN_WEIGHTS)
    assert result.value == compute_palma_ratio(UNEVEN_SERVICE, UNEVEN_WEIGHTS)


def test_concentration_index_result_value_matches_compute_ci():
    result = concentration_index_result(UNEVEN_SERVICE, UNEVEN_RANK, UNEVEN_WEIGHTS)
    assert result.value == compute_concentration_index(
        UNEVEN_SERVICE, UNEVEN_RANK, UNEVEN_WEIGHTS
    )


def test_palma_result_inf_matches_compute_palma():
    values = np.array([0.0, 0.0, 0.0, 0.0, 10.0])
    weights = np.array([40.0, 20.0, 20.0, 10.0, 10.0])
    result = palma_result(values, weights)
    assert result.value == float("inf")
    assert result.value == compute_palma_ratio(values, weights)
    assert result.warnings


def test_zero_service_result_values_match_compute_functions():
    gini = gini_result(ZERO_SERVICE, EQUAL_WEIGHTS)
    palma = palma_result(ZERO_SERVICE, EQUAL_WEIGHTS)
    ci = concentration_index_result(ZERO_SERVICE[:3], UNEVEN_RANK[:3], EQUAL_WEIGHTS[:3])
    assert gini.value == compute_gini(ZERO_SERVICE, EQUAL_WEIGHTS) == pytest.approx(0.0)
    assert palma.value == compute_palma_ratio(ZERO_SERVICE, EQUAL_WEIGHTS) == pytest.approx(1.0)
    assert ci.value == compute_concentration_index(
        ZERO_SERVICE[:3], UNEVEN_RANK[:3], EQUAL_WEIGHTS[:3]
    ) == pytest.approx(0.0)


def test_zero_service_conventions_emit_warnings():
    gini = gini_result(ZERO_SERVICE, EQUAL_WEIGHTS)
    palma = palma_result(ZERO_SERVICE, EQUAL_WEIGHTS)
    ci = concentration_index_result(ZERO_SERVICE[:3], UNEVEN_RANK[:3], EQUAL_WEIGHTS[:3])
    assert gini.warnings
    assert palma.warnings
    assert ci.warnings
    assert gini.metric == "gini"
    assert palma.metric == "palma"
    assert ci.metric == "ci"


def test_ci_zero_population_units_are_dropped():
    service = np.array([1.0, 99.0, 5.0])
    rank = np.array([1.0, 99.0, 2.0])
    population = np.array([100.0, 0.0, 100.0])
    result = concentration_index_result(service, rank, population)
    assert result.n_dropped == 1
    assert result.n_areas == 2
    assert result.total_population == pytest.approx(200.0)
    assert result.value == compute_concentration_index(service, rank, population)


def test_gini_zero_weight_unit_is_dropped_from_counts():
    values = np.array([1.0, 2.0, 5.0])
    weights = np.array([1.0, 0.0, 3.0])
    result = gini_result(values, weights)
    assert result.n_dropped == 1
    assert result.n_areas == 2
    assert result.total_population == pytest.approx(4.0)
    assert result.value == compute_gini(values, weights)


def test_live_units_have_no_drops():
    result = gini_result(EQUAL_SERVICE, EQUAL_WEIGHTS)
    assert result.n_areas == 4
    assert result.n_dropped == 0
    assert result.total_population == pytest.approx(400.0)
    assert result.warnings == []


def test_method_ids_and_palma_parameters():
    gini = gini_result(EQUAL_SERVICE, EQUAL_WEIGHTS)
    palma = palma_result(EQUAL_SERVICE, EQUAL_WEIGHTS)
    ci = concentration_index_result(UNEVEN_SERVICE, UNEVEN_RANK, UNEVEN_WEIGHTS)
    assert gini.method == "lorenz-trapezoid"
    assert palma.method == "palma-split-40-90"
    assert ci.method == "wagstaff-covariance"
    assert palma.parameters["bottom_cut"] == pytest.approx(0.40)
    assert palma.parameters["top_cut"] == pytest.approx(0.90)


def test_context_defaults_and_passthrough():
    bare = gini_result(EQUAL_SERVICE, EQUAL_WEIGHTS)
    assert bare.context == {}
    tagged = palma_result(EQUAL_SERVICE, EQUAL_WEIGHTS, context={"city": "leeds"})
    assert tagged.context == {"city": "leeds"}


def test_equity_result_is_frozen():
    result = gini_result(EQUAL_SERVICE, EQUAL_WEIGHTS)
    assert isinstance(result, EquityResult)
    with pytest.raises(AttributeError):
        result.value = 0.5  # type: ignore[misc]


def test_to_dict_round_trip_shape():
    result = gini_result(UNEVEN_SERVICE, UNEVEN_WEIGHTS, context={"region": "north"})
    data = result.to_dict()
    assert set(data) == TO_DICT_KEYS
    assert data["metric"] == "gini"
    assert data["value"] == result.value
    assert data["method"] == result.method
    assert data["n_areas"] == result.n_areas
    assert data["n_dropped"] == result.n_dropped
    assert data["total_population"] == result.total_population
    assert data["parameters"] == result.parameters
    assert data["warnings"] == result.warnings
    assert data["note"] == result.note
    assert data["context"] == {"region": "north"}


def test_to_dict_preserves_palma_inf():
    values = np.array([0.0, 0.0, 0.0, 0.0, 10.0])
    weights = np.array([40.0, 20.0, 20.0, 10.0, 10.0])
    data = palma_result(values, weights).to_dict()
    assert math.isinf(data["value"])
    assert data["metric"] == "palma"
