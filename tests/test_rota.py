"""The rota page must not speak in statistical vocabulary, and the reply must not either."""

import importlib.util
import json
from pathlib import Path

_ROTA = Path(__file__).resolve().parents[1] / "everyday" / "rota.py"
_SPEC = importlib.util.spec_from_file_location("everyday_rota", _ROTA)
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
advise = _MODULE.advise


def test_unequal_hours_become_an_action():
    result = advise(
        [
            {"name": "Alex", "hours": 2},
            {"name": "Sam", "hours": 2},
            {"name": "Jo", "hours": 2},
            {"name": "Riley", "hours": 18},
        ]
    )
    assert result["action"] == (
        "Riley did about three times their share of the hours. "
        "Give the next long duty to someone else."
    )
    text = json.dumps(result).lower()
    for banned in ("gini", "palma", "concentration", "coefficient"):
        assert banned not in text


def test_equal_hours_say_keep_sharing():
    result = advise(
        [
            {"name": "Alex", "hours": 5},
            {"name": "Sam", "hours": 5},
        ]
    )
    assert result["action"] == "The hours match. Keep sharing the duties as you are."


def test_missing_hours_are_not_zero_and_can_change_the_answer():
    result = advise(
        [
            {"name": "Alex", "hours": 2},
            {"name": "Sam", "hours": None},
            {"name": "Jo", "hours": 2},
            {"name": "Riley", "hours": 18},
        ]
    )
    assert "Sam had no hours" in result["action"]
    assert "not treated as zero" in " ".join(result["assumptions"])
    assert "can change" in " ".join(result["assumptions"])


def test_rota_page_has_no_statistical_vocabulary():
    page = (Path(__file__).resolve().parents[1] / "website" / "rota" / "index.html").read_text(
        encoding="utf-8"
    )
    main = page.split("<main", 1)[1].split("</main>", 1)[0].lower()
    for banned in ("gini", "palma", "concentration", "coefficient"):
        assert banned not in main
    assert "Nothing you type is stored" in page
    assert "language validated" not in page.lower()
