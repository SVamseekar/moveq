"""``moveq`` command-line tool.

    moveq gini data.csv --value trips --weight population
    moveq palma data.csv --value trips --weight population
    moveq ci data.csv --value trips --rank deprivation_rank --weight population
    moveq score --terms '{"coverage": 0.8, "evening": 0.5}' --weights '{"coverage": 0.6, "evening": 0.4}'
    moveq score config.json
    moveq catalogue validate config.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from moveq_catalogue import Catalogue, SectionAction
from moveq_core import (
    EquityResult,
    compute_score,
    concentration_index_result,
    gini_result,
    palma_result,
)


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


def _print_equity(result: EquityResult, label: str, as_json: bool) -> int:
    if as_json:
        print(json.dumps(result.to_dict(), indent=2))
        return 0
    print(f"{label}: {result.value:.4f}")
    return 0


def _cmd_gini(args: argparse.Namespace) -> int:
    cols = _read_columns(args.csv, [args.value, args.weight])
    return _print_equity(gini_result(cols[args.value], cols[args.weight]), "gini", args.json)


def _cmd_palma(args: argparse.Namespace) -> int:
    cols = _read_columns(args.csv, [args.value, args.weight])
    return _print_equity(palma_result(cols[args.value], cols[args.weight]), "palma", args.json)


def _cmd_ci(args: argparse.Namespace) -> int:
    cols = _read_columns(args.csv, [args.value, args.rank, args.weight])
    return _print_equity(
        concentration_index_result(cols[args.value], cols[args.rank], cols[args.weight]),
        "concentration_index",
        args.json,
    )


def _cmd_score(args: argparse.Namespace) -> int:
    terms: dict[str, Any] = {}
    weights: dict[str, float] = {}
    labels: dict[str, str] | None = None
    n_areas: int | None = None
    context: dict[str, str] | None = None

    if args.config:
        with open(args.config, encoding="utf-8") as fh:
            data = json.load(fh)
        terms = data.get("terms", {})
        weights = data.get("weights", {})
        labels = data.get("labels")
        n_areas = data.get("n_areas")
        context = data.get("context")
    else:
        if not args.terms or not args.weights:
            raise ValueError("Either provide a config file or both --terms and --weights arguments")
        terms = json.loads(args.terms)
        weights = json.loads(args.weights)
        if args.labels:
            labels = json.loads(args.labels)
        if args.context:
            context = json.loads(args.context)
        n_areas = args.n_areas

    result = compute_score(
        terms=terms,
        weights=weights,
        labels=labels,
        n_areas=n_areas,
        context=context,
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
        return 0

    if result.score is None:
        print("score: None")
    else:
        print(f"score: {result.score:.1f}")

    if result.note:
        print(f"note: {result.note}")

    print("components:")
    for comp in result.components:
        if comp.missing:
            print(f"  - {comp.id} ({comp.label}): missing, design_weight={comp.design_weight:.2f}")
        else:
            print(
                f"  - {comp.id} ({comp.label}): value={comp.value:.4f}, "
                f"design_weight={comp.design_weight:.2f}, weight_used={comp.weight_used:.4f}"
            )
    return 0


def _cmd_catalogue_validate(args: argparse.Namespace) -> int:
    with open(args.config, encoding="utf-8") as fh:
        data = json.load(fh)

    country = data.get("country")
    if not country:
        raise ValueError("Catalogue config missing required 'country' field")

    base_sections = data.get("base_sections")
    if not base_sections or not isinstance(base_sections, list):
        raise ValueError("Catalogue config missing or invalid 'base_sections' list")

    catalogue = Catalogue(base_sections, country=country)

    for item in data.get("mappings", []):
        section_id = item.get("section_id")
        action_str = item.get("action")
        if not section_id or not action_str:
            raise ValueError(f"Mapping item missing section_id or action: {item}")
        action = SectionAction(action_str)
        catalogue.register(
            section_id,
            action,
            note=item.get("note"),
            replacement_title=item.get("replacement_title"),
        )

    issues = catalogue.validate()

    if args.json:
        out = catalogue.to_dict()
        out["issues"] = issues
        out["valid"] = len(issues) == 0
        print(json.dumps(out, indent=2))
        return 0 if not issues else 1

    summary = catalogue.summary()
    print(f"country: {country}")
    print(f"summary: same={summary['same']}, replace={summary['replace']}, omit={summary['omit']}")

    if issues:
        print("validation errors:")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("status: valid (fully specified)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="moveq", description="Transport-equity metrics and catalogue tools.")
    sub = parser.add_subparsers(dest="command", required=True)

    # Gini
    gini = sub.add_parser("gini", help="Population-weighted Gini coefficient")
    gini.add_argument("csv", help="Path to input CSV file")
    gini.add_argument("--value", required=True, help="Service-level column")
    gini.add_argument("--weight", required=True, help="Population-weight column")
    gini.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    gini.set_defaults(func=_cmd_gini)

    # Palma
    palma = sub.add_parser("palma", help="Palma ratio (top 10%% / bottom 40%%)")
    palma.add_argument("csv", help="Path to input CSV file")
    palma.add_argument("--value", required=True, help="Service-level column")
    palma.add_argument("--weight", required=True, help="Population-weight column")
    palma.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    palma.set_defaults(func=_cmd_palma)

    # Concentration Index
    ci = sub.add_parser("ci", help="Wagstaff Concentration Index")
    ci.add_argument("csv", help="Path to input CSV file")
    ci.add_argument("--value", required=True, help="Service-level column")
    ci.add_argument("--rank", required=True, help="Ranking column (e.g. deprivation rank)")
    ci.add_argument("--weight", required=True, help="Population-weight column")
    ci.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    ci.set_defaults(func=_cmd_ci)

    # Score
    score = sub.add_parser("score", help="Compute weighted composite score with graceful missing-term handling")
    score.add_argument("config", nargs="?", default=None, help="Path to JSON configuration file")
    score.add_argument("--terms", help="JSON dictionary of terms: e.g. '{\"coverage\": 0.8}'")
    score.add_argument("--weights", help="JSON dictionary of design weights: e.g. '{\"coverage\": 0.5}'")
    score.add_argument("--labels", help="JSON dictionary of human-readable labels")
    score.add_argument("--context", help="JSON dictionary of free-form context")
    score.add_argument("--n-areas", type=int, help="Count of areal units")
    score.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    score.set_defaults(func=_cmd_score)

    # Catalogue
    cat_parser = sub.add_parser("catalogue", help="Cross-country catalogue harmonization tools")
    cat_sub = cat_parser.add_subparsers(dest="subcommand", required=True)

    cat_val = cat_sub.add_parser("validate", help="Validate a country's section catalogue against base sections")
    cat_val.add_argument("config", help="Path to JSON catalogue configuration file")
    cat_val.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    cat_val.set_defaults(func=_cmd_catalogue_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
