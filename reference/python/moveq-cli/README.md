# moveq-cli

Command-line interface for [`moveq`](https://pypi.org/project/moveq/): compute
equity metrics, composite accessibility scores, and validate country
harmonization catalogues from CSV or JSON without writing Python.

[![PyPI](https://img.shields.io/pypi/v/moveq-cli.svg)](https://pypi.org/project/moveq-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/moveq-cli.svg)](https://pypi.org/project/moveq-cli/)
[![License](https://img.shields.io/pypi/l/moveq-cli.svg)](https://github.com/SVamseekar/moveq/blob/main/LICENSE)

## Installation

Requires Python 3.10+.

```bash
pip install moveq-cli
```

This installs the `moveq` console script and pulls in `moveq` (and therefore
`moveq-core` and `moveq-catalogue`).

## Commands

### Inequality metrics from CSV

```bash
moveq gini data.csv --value trips --weight population
moveq palma data.csv --value trips --weight population
moveq ci data.csv --value trips --rank deprivation_rank --weight population
```

### Composite scoring

```bash
moveq score --terms '{"coverage": 0.8, "evening": 0.5, "frequency": null}' \
            --weights '{"coverage": 0.5, "evening": 0.3, "frequency": 0.2}'

moveq score score_config.json --json
```

### Catalogue validation

```bash
moveq catalogue validate country_catalogue.json
```

## Documentation

- [Getting started & CLI guide](https://github.com/SVamseekar/moveq/blob/main/docs/getting_started.md)
- [API reference](https://github.com/SVamseekar/moveq/blob/main/docs/api_reference.md)
- [Source repository](https://github.com/SVamseekar/moveq)
- [Changelog](https://github.com/SVamseekar/moveq/blob/main/CHANGELOG.md)

## License

[BSD 3-Clause](https://github.com/SVamseekar/moveq/blob/main/LICENSE).
