"""Docs keep distribution, uncertainty, mechanism, and cause apart."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
METHODOLOGY = ROOT / "docs" / "methodology.md"


def test_methodology_separates_the_four_layers():
    text = METHODOLOGY.read_text(encoding="utf-8")
    assert "Observed distribution" in text
    assert "Statistical uncertainty" in text
    assert "Possible mechanisms" in text
    assert "Causal attribution" in text
    assert "not a finding of discrimination" in text
    assert "not evidence that an intervention caused" in text
