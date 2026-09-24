"""The constructed pair is a demonstration. The mean can rise while the bottom falls."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[4]
    / "examples"
    / "distributional_difference"
    / "run.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("distributional_difference", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_mean_rises_while_bottom_share_falls_with_an_interval():
    row = _load().demonstrate()
    assert row["label"] == "demonstration"
    assert row["mean_proposal"] > row["mean_baseline"]
    assert row["bottom_share_proposal"] < row["bottom_share_baseline"]
    assert row["ci_low"] <= row["difference"] <= row["ci_high"]
    text = SCRIPT.read_text(encoding="utf-8")
    assert "not a shipped" in text
    assert "DEMONSTRATION" in text
