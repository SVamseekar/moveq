import csv
import io
import json
from contextlib import redirect_stderr, redirect_stdout

import pytest

from moveq_cli.main import main


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_gini_command(tmp_path):
    csv_path = tmp_path / "data.csv"
    _write_csv(
        csv_path,
        [{"trips": "10", "population": "100"}, {"trips": "10", "population": "100"}],
        ["trips", "population"],
    )
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["gini", str(csv_path), "--value", "trips", "--weight", "population"])
    assert code == 0
    assert buf.getvalue() == "gini: 0.0000\n"


def test_gini_json_contains_metric_and_value(tmp_path):
    csv_path = tmp_path / "data.csv"
    _write_csv(
        csv_path,
        [{"trips": "10", "population": "100"}, {"trips": "10", "population": "100"}],
        ["trips", "population"],
    )
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(
            ["gini", str(csv_path), "--value", "trips", "--weight", "population", "--json"]
        )
    assert code == 0
    data = json.loads(buf.getvalue())
    assert data["metric"] == "gini"
    assert data["value"] == pytest.approx(0.0)


def test_palma_command(tmp_path):
    csv_path = tmp_path / "data.csv"
    _write_csv(
        csv_path,
        [{"trips": str(i * 10), "population": "100"} for i in range(1, 11)],
        ["trips", "population"],
    )
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["palma", str(csv_path), "--value", "trips", "--weight", "population"])
    assert code == 0
    assert "palma:" in buf.getvalue()


def test_ci_command(tmp_path):
    csv_path = tmp_path / "data.csv"
    _write_csv(
        csv_path,
        [
            {"trips": "10", "dep_rank": "1", "population": "100"},
            {"trips": "20", "dep_rank": "2", "population": "100"},
        ],
        ["trips", "dep_rank", "population"],
    )
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "ci",
                str(csv_path),
                "--value",
                "trips",
                "--rank",
                "dep_rank",
                "--weight",
                "population",
                "--rank-direction",
                "higher-is-advantaged",
            ]
        )
    assert code == 0
    out = buf.getvalue()
    assert "concentration_index:" in out
    assert "{" not in out


def test_palma_json_contains_metric_and_value(tmp_path):
    csv_path = tmp_path / "data.csv"
    _write_csv(
        csv_path,
        [{"trips": str(i * 10), "population": "100"} for i in range(1, 11)],
        ["trips", "population"],
    )
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(
            ["palma", str(csv_path), "--value", "trips", "--weight", "population", "--json"]
        )
    assert code == 0
    data = json.loads(buf.getvalue())
    assert data["metric"] == "palma"
    assert isinstance(data["value"], float)


def test_ci_json_contains_metric_and_value(tmp_path):
    csv_path = tmp_path / "data.csv"
    _write_csv(
        csv_path,
        [
            {"trips": "10", "dep_rank": "1", "population": "100"},
            {"trips": "20", "dep_rank": "2", "population": "100"},
        ],
        ["trips", "dep_rank", "population"],
    )
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "ci",
                str(csv_path),
                "--value",
                "trips",
                "--rank",
                "dep_rank",
                "--weight",
                "population",
                "--rank-direction",
                "higher-is-advantaged",
                "--json",
            ]
        )
    assert code == 0
    data = json.loads(buf.getvalue())
    assert data["metric"] == "ci"
    assert isinstance(data["value"], float)


def test_missing_column_returns_error(tmp_path):
    csv_path = tmp_path / "data.csv"
    _write_csv(csv_path, [{"trips": "10"}], ["trips"])
    code = main(["gini", str(csv_path), "--value", "trips", "--weight", "population"])
    assert code == 1


def test_score_inline_args():
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main([
            "score",
            "--terms",
            '{"coverage": 0.8, "evening": 0.5, "frequency": null}',
            "--weights",
            '{"coverage": 0.5, "evening": 0.3, "frequency": 0.2}',
        ])
    assert code == 0
    out = buf.getvalue()
    assert "score: 68.8" in out
    assert "renormalised" in out


def test_score_json_config(tmp_path):
    config_path = tmp_path / "score_config.json"
    config_path.write_text(
        json.dumps({
            "terms": {"coverage": 0.8, "evening": 0.5},
            "weights": {"coverage": 0.6, "evening": 0.4},
        }),
        encoding="utf-8",
    )
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["score", str(config_path), "--json"])
    assert code == 0
    data = json.loads(buf.getvalue())
    assert data["score"] == 68.0


def test_score_missing_arguments():
    code = main(["score"])
    assert code == 1


def test_catalogue_validate_valid(tmp_path):
    cat_path = tmp_path / "catalogue.json"
    cat_path.write_text(
        json.dumps({
            "country": "france",
            "base_sections": ["s1", "s2", "s3"],
            "mappings": [
                {"section_id": "s1", "action": "same"},
                {"section_id": "s2", "action": "replace", "replacement_title": "Local S2"},
                {"section_id": "s3", "action": "omit", "note": "No census data available"},
            ],
        }),
        encoding="utf-8",
    )
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["catalogue", "validate", str(cat_path)])
    assert code == 0
    assert "status: valid (fully specified)" in buf.getvalue()


def test_catalogue_validate_invalid_unmapped(tmp_path):
    cat_path = tmp_path / "catalogue_unmapped.json"
    cat_path.write_text(
        json.dumps({
            "country": "france",
            "base_sections": ["s1", "s2"],
            "mappings": [
                {"section_id": "s1", "action": "same"},
            ],
        }),
        encoding="utf-8",
    )
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["catalogue", "validate", str(cat_path), "--json"])
    assert code == 1
    data = json.loads(buf.getvalue())
    assert data["valid"] is False
    assert len(data["issues"]) == 1


def test_ci_missing_rank_direction_exits_nonzero(tmp_path):
    csv_path = tmp_path / "data.csv"
    _write_csv(
        csv_path,
        [
            {"trips": "10", "dep_rank": "1", "population": "100"},
            {"trips": "20", "dep_rank": "2", "population": "100"},
        ],
        ["trips", "dep_rank", "population"],
    )
    with pytest.raises(SystemExit) as excinfo:
        main(
            [
                "ci",
                str(csv_path),
                "--value",
                "trips",
                "--rank",
                "dep_rank",
                "--weight",
                "population",
            ]
        )
    assert excinfo.value.code != 0


def test_ci_invalid_rank_direction_exits_2(tmp_path):
    csv_path = tmp_path / "data.csv"
    _write_csv(
        csv_path,
        [
            {"trips": "10", "dep_rank": "1", "population": "100"},
            {"trips": "20", "dep_rank": "2", "population": "100"},
        ],
        ["trips", "dep_rank", "population"],
    )
    with pytest.raises(SystemExit) as excinfo:
        main(
            [
                "ci",
                str(csv_path),
                "--value",
                "trips",
                "--rank",
                "dep_rank",
                "--weight",
                "population",
                "--rank-direction",
                "sideways",
            ]
        )
    assert excinfo.value.code == 2


def test_ci_reversed_rank_with_flipped_direction_matches(tmp_path):
    csv_a = tmp_path / "a.csv"
    csv_b = tmp_path / "b.csv"
    _write_csv(
        csv_a,
        [
            {"trips": "10", "dep_rank": "1", "population": "100"},
            {"trips": "20", "dep_rank": "2", "population": "100"},
            {"trips": "30", "dep_rank": "3", "population": "100"},
            {"trips": "40", "dep_rank": "4", "population": "100"},
        ],
        ["trips", "dep_rank", "population"],
    )
    _write_csv(
        csv_b,
        [
            {"trips": "10", "dep_rank": "4", "population": "100"},
            {"trips": "20", "dep_rank": "3", "population": "100"},
            {"trips": "30", "dep_rank": "2", "population": "100"},
            {"trips": "40", "dep_rank": "1", "population": "100"},
        ],
        ["trips", "dep_rank", "population"],
    )
    buf_a = io.StringIO()
    buf_b = io.StringIO()
    with redirect_stdout(buf_a):
        code_a = main(
            [
                "ci",
                str(csv_a),
                "--value",
                "trips",
                "--rank",
                "dep_rank",
                "--weight",
                "population",
                "--rank-direction",
                "higher-is-advantaged",
            ]
        )
    with redirect_stdout(buf_b):
        code_b = main(
            [
                "ci",
                str(csv_b),
                "--value",
                "trips",
                "--rank",
                "dep_rank",
                "--weight",
                "population",
                "--rank-direction",
                "higher-is-disadvantaged",
            ]
        )
    assert code_a == 0
    assert code_b == 0
    assert buf_a.getvalue() == buf_b.getvalue()


def test_ci_undefined_exits_3(tmp_path):
    csv_path = tmp_path / "data.csv"
    _write_csv(
        csv_path,
        [
            {"trips": "0", "dep_rank": "1", "population": "100"},
            {"trips": "0", "dep_rank": "2", "population": "100"},
        ],
        ["trips", "dep_rank", "population"],
    )
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(
            [
                "ci",
                str(csv_path),
                "--value",
                "trips",
                "--rank",
                "dep_rank",
                "--weight",
                "population",
                "--rank-direction",
                "higher-is-advantaged",
            ]
        )
    assert code == 3
    assert "undefined" in err.getvalue()

    buf = io.StringIO()
    with redirect_stdout(buf):
        json_code = main(
            [
                "ci",
                str(csv_path),
                "--value",
                "trips",
                "--rank",
                "dep_rank",
                "--weight",
                "population",
                "--rank-direction",
                "higher-is-advantaged",
                "--json",
            ]
        )
    assert json_code == 3
    data = json.loads(buf.getvalue())
    assert data["value"] is None
    assert data["status"] == "undefined"


def test_help_command():
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0

