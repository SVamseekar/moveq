# moveq

**Python libraries for transport-equity analysis.**

`moveq` turns raw service and demographic data — trips per area, population counts, deprivation ranks — into standard inequality measures (Gini, Palma, Wagstaff Concentration Index), a configurable composite accessibility score, and a cross-country harmonization registry for extending methodologies without silent omissions.

It is a library stack, not a hosted product:

- **Modular & lightweight**: installable Python packages with no framework lock-in.
- **Pure NumPy core**: zero required I/O or GIS dependencies (`moveq-core`).
- **Standardized CLI**: quick CSV-in, numbers-out command-line interface (`moveq-cli`).
- **Harmonization registry**: programmatic `same`/`replace`/`omit` contracts for cross-country studies (`moveq-catalogue`).

`moveq` computes what the data shows. It does not decide policy — you keep that judgment; `moveq` owns the math and the trail of what was computed.

---

## Documentation

Comprehensive documentation and guides are available in the [`docs/`](docs/) directory:

- [**Overview & Architecture**](docs/index.md)
- [**Methodology & Mathematical Formulations**](docs/methodology.md) (Gini, Palma, Concentration Index, Composite Scoring)
- [**Getting Started & CLI Guide**](docs/getting_started.md)
- [**Cross-Country Catalogue Harmonization Guide**](docs/catalogue_guide.md)
- [**API Reference**](docs/api_reference.md)

---

## Packages

| Package | What it is |
| --- | --- |
| [`moveq-core`](reference/python/moveq-core/) | Gini, Palma, Concentration Index, weighted composite scoring, vulnerability indexing |
| [`moveq-catalogue`](reference/python/moveq-catalogue/) | Same/replace/omit registry for cross-country section catalogues |
| [`moveq`](reference/python/moveq/) | Umbrella package re-exporting both |
| [`moveq-cli`](reference/python/moveq-cli/) | `moveq` command-line tool |

---

## Installation (from source)

```bash
git clone <this-repo>
cd moveq
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all packages in editable mode
pip install -e reference/python/moveq-core
pip install -e reference/python/moveq-catalogue
pip install -e reference/python/moveq
pip install -e reference/python/moveq-cli

# Optional: install pandas support for DataFrame helpers
pip install -e "reference/python/moveq-core[frames]"
```

---

## Quickstart

### Python API

```python
import numpy as np
from moveq import (
    compute_gini,
    compute_palma_ratio,
    compute_concentration_index,
    compute_score,
)

service = np.array([10.0, 20.0, 5.0, 50.0, 8.0])
population = np.array([1000, 800, 1200, 300, 900])
deprivation_rank = np.array([1, 3, 2, 5, 4])  # 1 = most deprived

# 1. Inequality metrics
gini = compute_gini(service, population)
palma = compute_palma_ratio(service, population)
ci = compute_concentration_index(service, deprivation_rank, population)

print(f"Gini: {gini:.4f}")
print(f"Palma Ratio: {palma:.4f}")
print(f"Concentration Index: {ci:.4f}")

# 2. Composite scoring (with graceful missing-term handling)
result = compute_score(
    terms={"coverage": 0.7, "evening": 0.5, "frequency": None, "gap": 0.9},
    weights={"coverage": 0.40, "evening": 0.25, "frequency": 0.20, "gap": 0.15},
    labels={"coverage": "400m Buffer", "evening": "Evening Service"},
)
print(result.to_dict())
```

### Command-Line Interface (CLI)

```bash
# Equity metrics from CSV
moveq gini examples/basic_equity/data.csv --value trips --weight population
moveq palma examples/basic_equity/data.csv --value trips --weight population
moveq ci examples/basic_equity/data.csv --value trips --rank deprivation_rank --weight population

# Composite scoring
moveq score --terms '{"coverage": 0.8, "evening": 0.5}' --weights '{"coverage": 0.6, "evening": 0.4}'

# Catalogue validation
moveq catalogue validate country_catalogue.json
```

See [`examples/basic_equity/run.py`](examples/basic_equity/run.py) for a runnable end-to-end demo.

---

## Running Tests

Run the test suite using `pytest`:

```bash
pytest -v
```

CI/CD runs automatically across Python 3.10, 3.11, 3.12, and 3.13 via GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

---

## What moveq is not

- **Not a data pipeline or ingestion framework** — bring your own arrays or CSVs.
- **Not a hosted dashboard or SaaS product**.
- **Not tied to any single country's data sources** — algorithms are country-agnostic; `moveq-catalogue` manages the parts that aren't.

---

## Relationship to Aequitas

[Aequitas](https://github.com/) (the multi-country bus × deprivation briefing platform) is `moveq`'s flagship consumer and the origin of this methodology — `moveq` is the extraction of Aequitas's equity math and cross-country harmonization pattern into a standalone, reusable open-source library suite.

---

## License

[BSD 3-Clause](LICENSE).
