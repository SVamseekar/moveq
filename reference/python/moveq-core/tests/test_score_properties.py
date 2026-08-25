"""Composite-score properties against an independent renormalisation formula."""

import pytest

from moveq_core import compute_score

from oracles import composite_score

WEIGHTS = {"coverage": 0.40, "evening": 0.25, "frequency": 0.20, "gap": 0.15}


def test_full_terms_match_independent_weighted_sum():
    terms = {"coverage": 0.5, "evening": 0.25, "frequency": 0.8, "gap": 0.1}
    result = compute_score(terms, WEIGHTS)
    expected = composite_score(terms, WEIGHTS)
    assert result.score == pytest.approx(expected, abs=1e-12)


def test_missing_term_matches_independent_renormalisation():
    terms = {"coverage": 0.5, "evening": None, "frequency": 0.8, "gap": 0.1}
    result = compute_score(terms, WEIGHTS)
    expected = composite_score(terms, WEIGHTS)
    assert result.score == pytest.approx(expected, abs=1e-12)
    used = sum(c.weight_used for c in result.components if not c.missing)
    assert used == pytest.approx(1.0, abs=1e-12)


def test_clipped_terms_match_independent_clip():
    terms = {"coverage": 1.5, "evening": -0.5, "frequency": 0.5, "gap": 0.5}
    result = compute_score(terms, WEIGHTS)
    expected = composite_score(terms, WEIGHTS)
    assert result.score == pytest.approx(expected, abs=1e-12)


def test_all_missing_independent_score_is_none():
    terms = {"coverage": None, "evening": None, "frequency": None, "gap": None}
    assert composite_score(terms, WEIGHTS) is None
    assert compute_score(terms, WEIGHTS).score is None


def test_score_is_in_unit_interval_after_clip():
    terms = {"coverage": 2.0, "evening": -3.0, "frequency": 0.0, "gap": 1.0}
    result = compute_score(terms, WEIGHTS)
    assert result.score is not None
    assert 0.0 <= result.score <= 100.0


def test_equal_terms_give_that_value_times_100():
    terms = {"coverage": 0.4, "evening": 0.4, "frequency": 0.4, "gap": 0.4}
    result = compute_score(terms, WEIGHTS)
    assert result.score == pytest.approx(40.0, abs=1e-12)
    assert composite_score(terms, WEIGHTS) == pytest.approx(40.0, abs=1e-12)
