"""Spec 02: outcome_kind, weight_kind, missing_policy, CI variants."""

import numpy as np
import pytest

from moveq_core import (
    compute_concentration_index,
    compute_score,
    concentration_index_result,
    gini_result,
    palma_result,
)

from oracles import (
    composite_score,
    composite_score_as_zero,
    composite_score_bounds,
    concentration_index_erreygers,
    concentration_index_generalized,
    concentration_index_grouped,
    concentration_index_wagstaff_normalized,
    finite_or_equal,
)

UNEVEN_SERVICE = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
UNEVEN_WEIGHTS = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
UNEVEN_RANK = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
BINARY = np.array([0.0, 0.0, 1.0, 1.0])
BINARY_RANK = np.array([1.0, 2.0, 3.0, 4.0])
BINARY_POP = np.array([10.0, 10.0, 10.0, 10.0])
UNBOUNDED = np.array([0.0, 5.0, 10.0, 20.0])

WEIGHTS = {"access": 0.50, "frequency": 0.25, "climate": 0.25}
COMPLETE = {"access": 0.8, "frequency": 0.6, "climate": 0.4}
MISSING_CLIMATE = {"access": 0.8, "frequency": 0.6, "climate": None}


def test_outcome_kind_omitted_leaves_interpretation_none():
    result = concentration_index_result(
        UNEVEN_SERVICE, UNEVEN_RANK, UNEVEN_WEIGHTS,
        rank_direction="higher_is_advantaged",
        weight_kind="population",
    )
    assert result.interpretation is None
    assert "outcome_kind" not in result.parameters


def test_outcome_kind_records_location_not_fairness():
    result = concentration_index_result(
        UNEVEN_SERVICE, UNEVEN_RANK, UNEVEN_WEIGHTS,
        rank_direction="higher_is_advantaged",
        outcome_kind="benefit",
        weight_kind="population",
        context={"outcome": "Park access"},
    )
    assert result.parameters["outcome_kind"] == "benefit"
    assert result.interpretation == "Park access is concentrated among more-advantaged units."
    assert result.to_dict()["interpretation"] == result.interpretation
    banned = ("unfair", "unlawful", "pro-poor", "pro-rich", "discriminatory", "caused", "because", "disproportionately")
    low = result.interpretation.lower()
    assert not any(word in low for word in banned)


def test_outcome_kind_burden_uses_same_location_template():
    result = concentration_index_result(
        UNEVEN_SERVICE, UNEVEN_RANK, UNEVEN_WEIGHTS,
        rank_direction="higher_is_advantaged",
        outcome_kind="burden",
        weight_kind="population",
        context={"outcome": "Pollution"},
    )
    assert result.parameters["outcome_kind"] == "burden"
    assert result.interpretation == "Pollution is concentrated among more-advantaged units."


def test_outcome_kind_zero_ci_has_no_interpretation():
    equal = np.array([2.0, 2.0, 2.0, 2.0])
    result = concentration_index_result(
        equal, UNEVEN_RANK[:4], UNEVEN_WEIGHTS[:4],
        rank_direction="higher_is_advantaged",
        outcome_kind="benefit",
        weight_kind="population",
    )
    assert result.value == pytest.approx(0.0)
    assert result.interpretation is None
    assert result.parameters["outcome_kind"] == "benefit"


def test_scalar_ci_signature_unchanged():
    value = compute_concentration_index(
        UNEVEN_SERVICE, UNEVEN_RANK, UNEVEN_WEIGHTS,
        rank_direction="higher_is_advantaged",
    )
    assert value == concentration_index_result(
        UNEVEN_SERVICE, UNEVEN_RANK, UNEVEN_WEIGHTS,
        rank_direction="higher_is_advantaged",
        weight_kind="population",
        variant="standard",
    ).value


def test_weight_kind_on_all_three_result_apis():
    for fn in (gini_result, palma_result):
        omitted = fn(UNEVEN_SERVICE, UNEVEN_WEIGHTS)
        explicit = fn(UNEVEN_SERVICE, UNEVEN_WEIGHTS, weight_kind="population")
        area = fn(UNEVEN_SERVICE, UNEVEN_WEIGHTS, weight_kind="area")
        assert omitted.parameters["weight_kind"] == "population"
        assert any("weight_kind omitted" in w for w in omitted.warnings)
        assert explicit.parameters["weight_kind"] == "population"
        assert not any("weight_kind omitted" in w for w in explicit.warnings)
        assert area.parameters["weight_kind"] == "area"
        assert omitted.value == pytest.approx(explicit.value)
        assert omitted.to_dict()["parameters"]["weight_kind"] == "population"

    omitted_ci = concentration_index_result(
        UNEVEN_SERVICE, UNEVEN_RANK, UNEVEN_WEIGHTS,
        rank_direction="higher_is_advantaged",
    )
    explicit_ci = concentration_index_result(
        UNEVEN_SERVICE, UNEVEN_RANK, UNEVEN_WEIGHTS,
        rank_direction="higher_is_advantaged",
        weight_kind="population",
    )
    assert omitted_ci.parameters["weight_kind"] == "population"
    assert any("weight_kind omitted" in w for w in omitted_ci.warnings)
    assert not any("weight_kind omitted" in w for w in explicit_ci.warnings)


def test_unweighted_does_not_replace_weights():
    ones = np.ones(5)
    declared = gini_result(UNEVEN_SERVICE, ones, weight_kind="unweighted")
    pop = gini_result(UNEVEN_SERVICE, ones, weight_kind="population")
    assert declared.value == pytest.approx(pop.value)
    assert declared.parameters["weight_kind"] == "unweighted"


def test_missing_policy_reweight_matches_independent_oracle():
    result = compute_score(MISSING_CLIMATE, WEIGHTS, missing_policy="reweight")
    assert result.score == pytest.approx(composite_score(MISSING_CLIMATE, WEIGHTS))
    assert result.parameters["missing_policy"] == "reweight"
    assert result.bounds is None
    assert result.dropped == ["climate"]


def test_missing_policy_as_zero_matches_independent_oracle():
    result = compute_score(MISSING_CLIMATE, WEIGHTS, missing_policy="as_zero")
    assert result.score == pytest.approx(composite_score_as_zero(MISSING_CLIMATE, WEIGHTS))
    assert result.score == pytest.approx(55.0)
    reweighted = compute_score(MISSING_CLIMATE, WEIGHTS, missing_policy="reweight")
    assert reweighted.score == pytest.approx(composite_score(MISSING_CLIMATE, WEIGHTS))
    # 73.33 vs 55.00 — the documented swing
    assert reweighted.score == pytest.approx(73.333333, rel=1e-4)


def test_missing_policy_exclude_returns_no_score():
    result = compute_score(MISSING_CLIMATE, WEIGHTS, missing_policy="exclude")
    assert result.score is None
    assert result.bounds is None
    assert result.note is not None
    assert "exclude" in result.note
    assert result.parameters["missing_policy"] == "exclude"


def test_missing_policy_bounds_with_missing_terms():
    result = compute_score(MISSING_CLIMATE, WEIGHTS, missing_policy="bounds")
    low, high = composite_score_bounds(MISSING_CLIMATE, WEIGHTS)
    assert result.score is None
    assert result.bounds == pytest.approx((low, high))
    assert result.to_dict()["bounds"] == [result.bounds[0], result.bounds[1]]
    assert result.score is None  # no midpoint


def test_missing_policy_bounds_complete_data_is_point_and_degenerate_interval():
    result = compute_score(COMPLETE, WEIGHTS, missing_policy="bounds")
    expected = composite_score(COMPLETE, WEIGHTS)
    assert result.score == pytest.approx(expected)
    assert result.bounds == pytest.approx((expected, expected))


def test_missing_policy_omission_warns_and_records_reweight():
    with pytest.warns(UserWarning, match="missing_policy omitted"):
        result = compute_score(COMPLETE, WEIGHTS)
    assert result.parameters["missing_policy"] == "reweight"
    assert result.to_dict()["parameters"]["missing_policy"] == "reweight"


def test_variant_default_is_standard_and_method_unchanged():
    result = concentration_index_result(
        BINARY, BINARY_RANK, BINARY_POP,
        rank_direction="higher_is_advantaged",
        weight_kind="population",
    )
    assert result.method == "wagstaff-covariance"
    assert result.parameters["variant"] == "standard"
    assert result.value == pytest.approx(
        concentration_index_grouped(BINARY, BINARY_RANK, BINARY_POP)
    )


def test_variant_generalized_matches_oracle():
    result = concentration_index_result(
        BINARY, BINARY_RANK, BINARY_POP,
        rank_direction="higher_is_advantaged",
        weight_kind="population",
        variant="generalized",
    )
    assert result.method == "wagstaff-covariance"
    assert result.parameters["variant"] == "generalized"
    assert result.value == pytest.approx(
        concentration_index_generalized(BINARY, BINARY_RANK, BINARY_POP)
    )


def test_variant_erreygers_matches_oracle():
    result = concentration_index_result(
        BINARY, BINARY_RANK, BINARY_POP,
        rank_direction="higher_is_advantaged",
        weight_kind="population",
        variant="erreygers",
    )
    assert result.value == pytest.approx(
        concentration_index_erreygers(BINARY, BINARY_RANK, BINARY_POP)
    )


def test_variant_wagstaff_normalized_matches_oracle():
    result = concentration_index_result(
        BINARY, BINARY_RANK, BINARY_POP,
        rank_direction="higher_is_advantaged",
        weight_kind="population",
        variant="wagstaff_normalized",
    )
    assert result.value == pytest.approx(
        concentration_index_wagstaff_normalized(BINARY, BINARY_RANK, BINARY_POP)
    )


def test_erreygers_undefined_outside_unit_interval():
    result = concentration_index_result(
        UNBOUNDED, BINARY_RANK, BINARY_POP,
        rank_direction="higher_is_advantaged",
        weight_kind="population",
        variant="erreygers",
    )
    assert result.value is None
    assert result.status == "undefined"
    assert result.reason == "variant_requires_unit_interval"


def test_bounded_outcome_warns_but_does_not_switch_variant():
    result = concentration_index_result(
        BINARY, BINARY_RANK, BINARY_POP,
        rank_direction="higher_is_advantaged",
        weight_kind="population",
        variant="standard",
    )
    assert any("does not switch variant" in w for w in result.warnings)
    assert result.parameters["variant"] == "standard"


def test_unbounded_outcome_has_no_variant_warning():
    result = concentration_index_result(
        UNBOUNDED, BINARY_RANK, BINARY_POP,
        rank_direction="higher_is_advantaged",
        weight_kind="population",
        variant="standard",
    )
    assert not any("does not switch variant" in w for w in result.warnings)


def test_constant_unit_interval_has_no_variant_warning():
    constant = np.array([0.4, 0.4, 0.4, 0.4])
    result = concentration_index_result(
        constant, BINARY_RANK, BINARY_POP,
        rank_direction="higher_is_advantaged",
        weight_kind="population",
    )
    assert not any("does not switch variant" in w for w in result.warnings)


def test_ci_variants_permutation_invariant():
    rng = np.random.default_rng(7)
    order = rng.permutation(BINARY.size)
    for variant in ("standard", "generalized", "erreygers", "wagstaff_normalized"):
        base = concentration_index_result(
            BINARY, BINARY_RANK, BINARY_POP,
            rank_direction="higher_is_advantaged",
            weight_kind="population",
            variant=variant,
        )
        shuffled = concentration_index_result(
            BINARY[order], BINARY_RANK[order], BINARY_POP[order],
            rank_direction="higher_is_advantaged",
            weight_kind="population",
            variant=variant,
        )
        assert finite_or_equal(base.value, shuffled.value)


def test_erreygers_closed_form_two_equal_groups():
    # Two equal-population groups, y in {0, 1}, perfect rank alignment.
    # Relative CI = 1 − μ? For y=(0,1), equal pop, μ=0.5, fractional ranks
    # 0.25 and 0.75: cov = 0.5*(0-0.5)*(0.25-0.5)+0.5*(1-0.5)*(0.75-0.5)=0.125
    # CI = 2*0.125/0.5 = 0.5; Erreygers = 4*0.5*0.5 = 1 (maximum).
    y = np.array([0.0, 1.0])
    r = np.array([1.0, 2.0])
    w = np.array([1.0, 1.0])
    result = concentration_index_result(
        y, r, w, rank_direction="higher_is_advantaged",
        weight_kind="population", variant="erreygers",
    )
    assert result.value == pytest.approx(1.0)
    assert concentration_index_erreygers(y, r, w) == pytest.approx(1.0)


def test_invalid_outcome_kind_and_zero_mean_raise():
    with pytest.raises(ValueError, match="outcome_kind"):
        concentration_index_result(
            BINARY, BINARY_RANK, BINARY_POP,
            rank_direction="higher_is_advantaged",
            outcome_kind="neutral",  # type: ignore[arg-type]
        )
    with pytest.raises(ValueError, match="zero_mean"):
        concentration_index_result(
            BINARY, BINARY_RANK, BINARY_POP,
            rank_direction="higher_is_advantaged",
            zero_mean="oops",  # type: ignore[arg-type]
        )
    with pytest.raises(ValueError, match="zero_mean"):
        compute_concentration_index(
            BINARY, BINARY_RANK, BINARY_POP,
            rank_direction="higher_is_advantaged",
            zero_mean="oops",  # type: ignore[arg-type]
        )


def test_disadvantage_concentrated_interpretation_and_default_name():
    y = np.array([1.0, 0.0, 0.0, 0.0])
    result = concentration_index_result(
        y, BINARY_RANK, BINARY_POP,
        rank_direction="higher_is_advantaged",
        outcome_kind="burden",
        weight_kind="population",
    )
    assert result.value is not None and result.value < 0
    assert result.interpretation == "The outcome is concentrated among less-advantaged units."


def test_wagstaff_normalized_undefined_outside_unit_and_at_mean_one():
    unbounded = concentration_index_result(
        UNBOUNDED, BINARY_RANK, BINARY_POP,
        rank_direction="higher_is_advantaged",
        weight_kind="population",
        variant="wagstaff_normalized",
    )
    assert unbounded.value is None
    assert unbounded.reason == "variant_requires_unit_interval"
    ones = np.ones(4)
    all_one = concentration_index_result(
        ones, BINARY_RANK, BINARY_POP,
        rank_direction="higher_is_advantaged",
        weight_kind="population",
        variant="wagstaff_normalized",
    )
    assert all_one.value is None
    assert all_one.status == "undefined"


def test_all_missing_as_zero_exclude_and_bounds():
    empty = {"access": None, "frequency": None, "climate": None}
    as_zero = compute_score(empty, WEIGHTS, missing_policy="as_zero")
    assert as_zero.score == pytest.approx(0.0)
    exclude = compute_score(empty, WEIGHTS, missing_policy="exclude")
    assert exclude.score is None
    bounds = compute_score(empty, WEIGHTS, missing_policy="bounds")
    assert bounds.score is None
    assert bounds.bounds == pytest.approx((0.0, 100.0))


def test_invalid_weight_kind_and_variant_raise():
    with pytest.raises(ValueError, match="weight_kind"):
        gini_result(UNEVEN_SERVICE, UNEVEN_WEIGHTS, weight_kind="households")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="variant"):
        concentration_index_result(
            BINARY, BINARY_RANK, BINARY_POP,
            rank_direction="higher_is_advantaged",
            variant="kakwani",  # type: ignore[arg-type]
        )
    with pytest.raises(ValueError, match="missing_policy"):
        compute_score(COMPLETE, WEIGHTS, missing_policy="impute")  # type: ignore[arg-type]
