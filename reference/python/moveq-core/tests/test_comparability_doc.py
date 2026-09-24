"""The general diff tool stays rejected in writing."""

from pathlib import Path

TEXT = (Path(__file__).resolve().parents[4] / "docs" / "comparability.md").read_text(
    encoding="utf-8"
)


def test_eight_questions_and_the_rejection():
    for marker in (
        "How is comparability verified?",
        "What happens when inputs are not comparable?",
        "difference interval",
        "areal unit or the population",
        "boundaries change",
        "moveq-cli",
        "small core",
        "What is the name?",
    ):
        assert marker in TEXT
    assert "not feasible" in TEXT
    assert "distributional difference" in TEXT
    assert "GitHub Action" in TEXT
