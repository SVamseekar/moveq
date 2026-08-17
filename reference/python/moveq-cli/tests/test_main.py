import csv
import io
from contextlib import redirect_stdout

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
    assert "gini: 0.0000" in buf.getvalue()


def test_missing_column_returns_error(tmp_path):
    csv_path = tmp_path / "data.csv"
    _write_csv(csv_path, [{"trips": "10"}], ["trips"])
    code = main(["gini", str(csv_path), "--value", "trips", "--weight", "population"])
    assert code == 1
