"""``moveq`` command-line tool.

    moveq gini data.csv --value trips --weight population
    moveq palma data.csv --value trips --weight population
    moveq ci data.csv --value trips --rank deprivation_rank --weight population
"""

from __future__ import annotations

import argparse
import csv
import sys

import numpy as np

from moveq_core import compute_concentration_index, compute_gini, compute_palma_ratio


def _read_columns(path: str, columns: list[str]) -> dict[str, np.ndarray]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path} has no data rows")
    missing = [c for c in columns if c not in rows[0]]
    if missing:
        raise ValueError(f"{path} is missing column(s): {', '.join(missing)}")
    return {c: np.array([float(r[c]) for r in rows]) for c in columns}


def _cmd_gini(args: argparse.Namespace) -> int:
    cols = _read_columns(args.csv, [args.value, args.weight])
    result = compute_gini(cols[args.value], cols[args.weight])
    print(f"gini: {result:.4f}")
    return 0


def _cmd_palma(args: argparse.Namespace) -> int:
    cols = _read_columns(args.csv, [args.value, args.weight])
    result = compute_palma_ratio(cols[args.value], cols[args.weight])
    print(f"palma: {result:.4f}")
    return 0


def _cmd_ci(args: argparse.Namespace) -> int:
    cols = _read_columns(args.csv, [args.value, args.rank, args.weight])
    result = compute_concentration_index(cols[args.value], cols[args.rank], cols[args.weight])
    print(f"concentration_index: {result:.4f}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="moveq", description="Transport-equity metrics from a CSV.")
    sub = parser.add_subparsers(dest="command", required=True)

    gini = sub.add_parser("gini", help="Population-weighted Gini coefficient")
    gini.add_argument("csv")
    gini.add_argument("--value", required=True, help="Service-level column")
    gini.add_argument("--weight", required=True, help="Population-weight column")
    gini.set_defaults(func=_cmd_gini)

    palma = sub.add_parser("palma", help="Palma ratio (top 10% / bottom 40%)")
    palma.add_argument("csv")
    palma.add_argument("--value", required=True, help="Service-level column")
    palma.add_argument("--weight", required=True, help="Population-weight column")
    palma.set_defaults(func=_cmd_palma)

    ci = sub.add_parser("ci", help="Wagstaff Concentration Index")
    ci.add_argument("csv")
    ci.add_argument("--value", required=True, help="Service-level column")
    ci.add_argument("--rank", required=True, help="Ranking column (e.g. deprivation rank)")
    ci.add_argument("--weight", required=True, help="Population-weight column")
    ci.set_defaults(func=_cmd_ci)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
