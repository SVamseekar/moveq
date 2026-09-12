def test_umbrella_reexports():
    from moveq import Catalogue, SectionAction, compute_gini, compute_score

    assert callable(compute_gini)
    assert callable(compute_score)
    assert SectionAction.SAME.value == "same"
    cat = Catalogue(["a"], country="test")
    assert cat.base_sections == ["a"]


def test_umbrella_reexports_equity_results():
    from moveq import (
        EquityResult,
        concentration_index_result,
        gini_result,
        palma_result,
    )

    assert EquityResult is not None
    assert callable(gini_result)
    assert callable(palma_result)
    assert callable(concentration_index_result)


def test_umbrella_reexports_evidence():
    from moveq import CLAIM_BADGES, validate_descriptor, validate_registry

    assert "blocked" in CLAIM_BADGES
    assert callable(validate_descriptor)
    assert callable(validate_registry)
