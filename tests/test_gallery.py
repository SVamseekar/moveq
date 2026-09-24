"""Gallery index matches the registry and commits no external extract."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gallery_cards_match_registry_badges():
    registry = json.loads((ROOT / "examples" / "evidence" / "registry.json").read_text())
    gallery = json.loads((ROOT / "website" / "assets" / "data" / "gallery.json").read_text())
    cards = [card for tier in gallery["tiers"] for card in tier["cards"]]
    by_id = {card["id"]: card for card in cards}
    assert set(by_id) == {case["id"] for case in registry["cases"]}
    for case in registry["cases"]:
        card = by_id[case["id"]]
        assert card["badge"] == case["claim"]
        assert card["extract"] is None
        assert card["question"]
    schemas = {tier["id"]: tier["schema"] for tier in gallery["tiers"]}
    assert "field" in schemas["research"]
    assert "question" in schemas["everyday"]
    assert "spec" not in schemas["everyday"]
    assert (ROOT / "examples" / "t1-2-gini-reporting" / "run.py").is_file()
    assert (ROOT / "examples" / "t2-7-household-load" / "run.py").is_file()
