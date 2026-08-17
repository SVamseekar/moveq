def test_umbrella_reexports():
    from moveq import Catalogue, SectionAction, compute_gini, compute_score

    assert callable(compute_gini)
    assert callable(compute_score)
    assert SectionAction.SAME.value == "same"
    cat = Catalogue(["a"], country="test")
    assert cat.base_sections == ["a"]
