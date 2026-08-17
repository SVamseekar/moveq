import pytest

from moveq_catalogue import Catalogue, SectionAction

BASE = ["coverage_pct", "service_deserts", "policy_scenarios"]


def test_same_action_registers_cleanly():
    cat = Catalogue(BASE, country="ireland")
    cat.register("coverage_pct", SectionAction.SAME, note="TFI x CSO Small Area")
    mapping = cat.mapping_for("coverage_pct")
    assert mapping.action is SectionAction.SAME
    assert mapping.country == "ireland"


def test_replace_without_title_raises():
    cat = Catalogue(BASE, country="ireland")
    with pytest.raises(ValueError, match="replacement_title"):
        cat.register("policy_scenarios", SectionAction.REPLACE)


def test_omit_without_note_raises():
    cat = Catalogue(BASE, country="ireland")
    with pytest.raises(ValueError, match="note"):
        cat.register("service_deserts", SectionAction.OMIT)


def test_register_unknown_section_raises():
    cat = Catalogue(BASE, country="ireland")
    with pytest.raises(ValueError, match="not in the base questionnaire"):
        cat.register("nonexistent", SectionAction.SAME)


def test_validate_flags_unregistered_sections():
    cat = Catalogue(BASE, country="ireland")
    cat.register("coverage_pct", SectionAction.SAME)
    issues = cat.validate()
    assert len(issues) == 1
    assert "service_deserts" in issues[0]
    assert "policy_scenarios" in issues[0]


def test_validate_passes_when_fully_mapped():
    cat = Catalogue(BASE, country="ireland")
    cat.register("coverage_pct", SectionAction.SAME)
    cat.register("service_deserts", SectionAction.OMIT, note="no free small-area variable")
    cat.register("policy_scenarios", SectionAction.REPLACE, replacement_title="Connecting Ireland")
    assert cat.validate() == []


def test_summary_counts_actions():
    cat = Catalogue(BASE, country="ireland")
    cat.register("coverage_pct", SectionAction.SAME)
    cat.register("service_deserts", SectionAction.SAME)
    cat.register("policy_scenarios", SectionAction.REPLACE, replacement_title="Connecting Ireland")
    assert cat.summary() == {"same": 2, "replace": 1, "omit": 0}


def test_duplicate_base_sections_raise():
    with pytest.raises(ValueError, match="duplicates"):
        Catalogue(["a", "a", "b"], country="ireland")
