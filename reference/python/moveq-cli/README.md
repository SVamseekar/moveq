# moveq-cli

Command-line tool for `moveq` — compute equity metrics, composite accessibility scores, and validate country harmonization catalogues from CSV or JSON without writing Python.

---

## Installation

```bash
pip install -e reference/python/moveq-cli
```

---

## Commands

### 1. Inequality Metrics from CSV

```bash
# Population-weighted Gini coefficient
moveq gini data.csv --value trips --weight population

# Palma ratio (top 10% / bottom 40%)
moveq palma data.csv --value trips --weight population

# Wagstaff Concentration Index
moveq ci data.csv --value trips --rank deprivation_rank --weight population
```

### 2. Composite Scoring

Compute weighted composite scores with dynamic missing-term handling:

```bash
# Using inline terms and weights:
moveq score --terms '{"coverage": 0.8, "evening": 0.5, "frequency": null}' --weights '{"coverage": 0.5, "evening": 0.3, "frequency": 0.2}'

# Using a JSON configuration file:
moveq score score_config.json --json
```

### 3. Catalogue Validation

Validate a country's section mappings against a base questionnaire:

```bash
moveq catalogue validate country_catalogue.json
```

---

## Documentation

See the root documentation:
- [Getting Started & CLI Guide](../../../docs/getting_started.md)
- [API Reference](../../../docs/api_reference.md)
