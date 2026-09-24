"""The everyday app must call moveq-core and retain nothing."""

from pathlib import Path

TEXT = (Path(__file__).resolve().parents[4] / "docs" / "everyday_app.md").read_text(
    encoding="utf-8"
)


def test_architecture_calls_core_and_retains_nothing():
    assert "moveq-core" in TEXT
    assert "JavaScript reimplementation" in TEXT
    assert "rejected" in TEXT
    assert "retain nothing" in TEXT
    assert "Server-side Python" in TEXT
    assert "recurring-duty rota" in TEXT
    assert "fair or unfair" in TEXT
