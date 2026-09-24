"""Small cells stay visible as suppressed. Omission leaves the result alone."""

import numpy as np
import pytest

from moveq_core import compute_gini, gini_result

VALUES = np.array([1.0, 4.0, 9.0])
WEIGHTS = np.array([2.0, 10.0, 10.0])


def test_omitted_suppress_below_matches_today():
    result = gini_result(VALUES, WEIGHTS, weight_kind="population")
    assert result.value == compute_gini(VALUES, WEIGHTS)
    assert "suppressed" not in " ".join(result.warnings)
    assert "suppress_below" not in result.parameters


def test_suppressed_cell_is_recorded_and_withheld():
    result = gini_result(
        VALUES, WEIGHTS, weight_kind="population", suppress_below=5
    )
    kept = gini_result(VALUES[1:], WEIGHTS[1:], weight_kind="population")
    assert result.value == pytest.approx(kept.value)
    assert result.parameters["suppress_below"] == 5
    assert result.parameters["suppressed_indices"] == [0]
    assert any("suppressed" in warning for warning in result.warnings)
    assert result.n_areas == 2
