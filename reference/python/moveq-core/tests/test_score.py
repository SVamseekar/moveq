import pytest

from moveq_core import compute_score

WEIGHTS = {"coverage": 0.40, "evening": 0.25, "frequency": 0.20, "gap": 0.15}
LABELS = {
    "coverage": "Share within 400m",
    "evening": "Evening service share",
    "frequency": "Weekday frequency",
    "gap": "Deprivation-service gap",
}


def test_full_terms_gives_expected_score():
    terms = {"coverage": 1.0, "evening": 1.0, "frequency": 1.0, "gap": 1.0}
    result = compute_score(terms, WEIGHTS, labels=LABELS)
    assert result.score == pytest.approx(100.0)
    assert result.dropped == []


def test_missing_term_is_dropped_and_weights_renormalised():
    terms = {"coverage": 1.0, "evening": 1.0, "frequency": None, "gap": 1.0}
    result = compute_score(terms, WEIGHTS, labels=LABELS)
    assert result.dropped == ["frequency"]
    # Remaining weights (0.40 + 0.25 + 0.15 = 0.80) renormalise to sum to 1.
    used = sum(c.weight_used for c in result.components if not c.missing)
    assert used == pytest.approx(1.0)
    assert result.score == pytest.approx(100.0)
    assert result.note is not None


def test_all_terms_missing_returns_none_score():
    terms = {"coverage": None, "evening": None, "frequency": None, "gap": None}
    result = compute_score(terms, WEIGHTS, labels=LABELS)
    assert result.score is None
    assert result.dropped == list(WEIGHTS)


def test_values_are_clipped_to_unit_interval():
    terms = {"coverage": 1.5, "evening": -0.5, "frequency": 0.5, "gap": 0.5}
    result = compute_score(terms, WEIGHTS, labels=LABELS)
    values = {c.id: c.value for c in result.components}
    assert values["coverage"] == 1.0
    assert values["evening"] == 0.0


def test_to_dict_rounds_score():
    terms = {"coverage": 0.333333, "evening": 1.0, "frequency": 1.0, "gap": 1.0}
    result = compute_score(terms, WEIGHTS, labels=LABELS, missing_policy="reweight")
    d = result.to_dict()
    assert isinstance(d["score"], float)
    assert d["score"] == round(d["score"], 1)
    assert "parameters" in d
    assert "bounds" in d


def test_rejects_zero_weight():
    terms = {"coverage": 1.0, "evening": 1.0, "frequency": 1.0, "gap": 1.0}
    bad_weights = {**WEIGHTS, "coverage": 0.0}
    with pytest.raises(ValueError):
        compute_score(terms, bad_weights, labels=LABELS)


def test_rejects_negative_weight():
    terms = {"coverage": 1.0, "evening": 1.0, "frequency": 1.0, "gap": 1.0}
    bad_weights = {**WEIGHTS, "coverage": -0.1}
    with pytest.raises(ValueError):
        compute_score(terms, bad_weights, labels=LABELS)


def test_rejects_non_finite_weight():
    terms = {"coverage": 1.0, "evening": 1.0, "frequency": 1.0, "gap": 1.0}
    bad_weights = {**WEIGHTS, "coverage": float("nan")}
    with pytest.raises(ValueError):
        compute_score(terms, bad_weights, labels=LABELS)


def test_rejects_non_finite_term():
    terms = {"coverage": float("nan"), "evening": 1.0, "frequency": 1.0, "gap": 1.0}
    with pytest.raises(ValueError, match="finite"):
        compute_score(terms, WEIGHTS, labels=LABELS)


def test_rejects_infinite_term():
    terms = {"coverage": float("inf"), "evening": 1.0, "frequency": 1.0, "gap": 1.0}
    with pytest.raises(ValueError, match="finite"):
        compute_score(terms, WEIGHTS, labels=LABELS)


def test_all_missing_preserves_n_areas():
    terms = {"coverage": None, "evening": None, "frequency": None, "gap": None}
    result = compute_score(terms, WEIGHTS, labels=LABELS, n_areas=12)
    assert result.score is None
    assert result.n_areas == 12


def test_all_missing_leaves_n_areas_none_when_omitted():
    terms = {"coverage": None, "evening": None, "frequency": None, "gap": None}
    result = compute_score(terms, WEIGHTS, labels=LABELS)
    assert result.n_areas is None
