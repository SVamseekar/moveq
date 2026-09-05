# moveq-cli

**Command-line interface for [moveq](https://pypi.org/project/moveq/).**

[![PyPI](https://img.shields.io/pypi/v/moveq-cli.svg)](https://pypi.org/project/moveq-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/moveq-cli.svg)](https://pypi.org/project/moveq-cli/)
[![License](https://img.shields.io/pypi/l/moveq-cli.svg)](https://github.com/SVamseekar/moveq/blob/main/LICENSE)

Use this package when you want the equity metrics, a composite
accessibility score, or a catalogue completeness check **from a
terminal** — a CSV of areas, or a JSON config — without writing Python.

`pip install moveq-cli` installs the `moveq` console script and pulls in
`moveq` (and therefore `moveq-core` and `moveq-catalogue`). The
algorithms are the same functions as the Python API; this package is
only the argparse front-end.

## What the commands do

**`moveq gini`** and **`moveq palma`** read a CSV and treat one column as
the service value (trips, departures, coverage) and another as the
population weight. By default they print a single number:

- Gini — overall inequality of that service across people (`0` = equal)
- Palma — mean service of the best-served 10% of population over the
  worst-served 40%, with boundary areas split proportionally (`1` =
  equal, including all-zero service; `inf` if the bottom 40% have no
  service and the top 10% do not)

**`moveq ci`** is the Wagstaff Concentration Index. It needs a rank
column and **`--rank-direction`** (`higher-is-advantaged` or
`higher-is-disadvantaged`). Positive values are advantage-concentrated;
negative values are disadvantage-concentrated. A zero or cancelled mean
exits with code `3`.

**`moveq score`** builds a 0–100 weighted composite. Terms live in
`[0, 1]`; JSON `null` means “this term was not collected.” The CLI still
uses the default `reweight` policy (drop missing terms and renormalise).
The Python API also offers `as_zero`, `exclude`, and `bounds`. You can
pass terms and weights on the command line or in a JSON file (`--json`).

**`moveq catalogue validate`** checks a country catalogue JSON against
the same / replace / omit rules: every base section must have an
explicit decision, replacements need a title, omissions need a note.

`moveq gini`, `moveq palma`, and `moveq ci` accept `--json` to print the
full `EquityResult` (`metric`, `value`, `method`, `n_areas`, warnings).
The default line is unchanged.

Column names are whatever your CSV actually uses; you point at them with
`--value`, `--weight`, and `--rank`.

## Installation

Requires Python 3.10+.

```bash
pip install moveq-cli
```

## Examples

Inequality from a CSV (headers `trips`, `population`, `deprivation_rank`):

```bash
moveq gini data.csv --value trips --weight population
moveq palma data.csv --value trips --weight population
moveq ci data.csv --value trips --rank deprivation_rank --weight population --rank-direction higher-is-advantaged
```

Composite score, inline or from a file:

```bash
moveq score \
  --terms '{"coverage": 0.8, "evening": 0.5, "frequency": null}' \
  --weights '{"coverage": 0.5, "evening": 0.3, "frequency": 0.2}'

moveq score score_config.json --json
```

Catalogue file:

```bash
moveq catalogue validate country_catalogue.json
```

## Documentation

- [Getting started and CLI guide](https://github.com/SVamseekar/moveq/blob/main/docs/getting_started.md)
- [Methodology](https://github.com/SVamseekar/moveq/blob/main/docs/methodology.md)
- [API reference](https://github.com/SVamseekar/moveq/blob/main/docs/api_reference.md)
- [Umbrella package](https://pypi.org/project/moveq/)
- [Source](https://github.com/SVamseekar/moveq)
- [Changelog](https://github.com/SVamseekar/moveq/blob/main/CHANGELOG.md)

## License

[BSD 3-Clause](https://github.com/SVamseekar/moveq/blob/main/LICENSE).
