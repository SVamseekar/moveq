# Getting Started with moveq

This guide covers installing `moveq`, running Python calculations, and using the `moveq` CLI.

---

## 1. Installation

### From Source (Editable Mode)

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/<org>/moveq.git
cd moveq
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all packages in editable mode
pip install -e reference/python/moveq-core
pip install -e reference/python/moveq-catalogue
pip install -e reference/python/moveq
pip install -e reference/python/moveq-cli
```

### Optional Dependencies

For pandas DataFrame helpers ([`moveq_core.frames`](file:///Users/souravamseekarmarti/Projects/moveq/reference/python/moveq-core/src/moveq_core/frames.py)):

```bash
pip install -e "reference/python/moveq-core[frames]"
```

For running tests:

```bash
pip install -e "reference/python/moveq-core[test]"
```

---

## 2. Python API Quickstart

### Computing Inequality Metrics

```python
import numpy as np
from moveq import (
    compute_gini,
    compute_palma_ratio,
    compute_concentration_index,
    compute_score,
)

# Sample spatial data
trips = np.array([12.0, 25.0, 4.0, 50.0, 8.0])
population = np.array([1200, 850, 1400, 300, 950])
deprivation_rank = np.array([1, 3, 2, 5, 4])  # 1 = most deprived

# 1. Population-weighted Gini coefficient
gini = compute_gini(trips, population)
print(f"Gini: {gini:.4f}")

# 2. Palma ratio (top 10% vs bottom 40%)
palma = compute_palma_ratio(trips, population)
print(f"Palma Ratio: {palma:.4f}")

# 3. Wagstaff Concentration Index
ci = compute_concentration_index(trips, deprivation_rank, population)
print(f"Concentration Index: {ci:.4f}")
```

### Composite Accessibility Scoring

```python
# Terms can have missing data (None)
terms = {
    "coverage_400m": 0.75,
    "evening_frequency": 0.50,
    "weekend_frequency": None,  # Not collected
    "affordability": 0.85,
}

weights = {
    "coverage_400m": 0.40,
    "evening_frequency": 0.25,
    "weekend_frequency": 0.20,
    "affordability": 0.15,
}

result = compute_score(
    terms=terms,
    weights=weights,
    labels={"coverage_400m": "400m Walking Buffer", "weekend_frequency": "Weekend Service"},
    n_areas=len(trips),
)

print(f"Score: {result.score:.1f} / 100")
print(f"Note: {result.note}")
print("Component Details:", result.to_dict())
```

---

## 3. Command-Line Interface (CLI)

The `moveq` CLI allows computing metrics directly from CSV files or JSON configurations without writing code.

### Metric Commands

```bash
# Gini coefficient
moveq gini data.csv --value trips --weight population

# Palma ratio
moveq palma data.csv --value trips --weight population

# Wagstaff Concentration Index
moveq ci data.csv --value trips --rank deprivation_rank --weight population
```

### Composite Scoring via CLI

```bash
# Inline terms & weights
moveq score --terms '{"coverage": 0.8, "frequency": null}' --weights '{"coverage": 0.7, "frequency": 0.3}'

# From a configuration file
moveq score score_config.json --json
```

### Cross-Country Catalogue Validation

```bash
moveq catalogue validate country_catalogue.json
```
