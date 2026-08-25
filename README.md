# moveq

**Python libraries for transport-equity analysis.**

[![CI](https://github.com/SVamseekar/moveq/actions/workflows/ci.yml/badge.svg)](https://github.com/SVamseekar/moveq/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/moveq.svg)](https://pypi.org/project/moveq/)
[![Python versions](https://img.shields.io/pypi/pyversions/moveq.svg)](https://pypi.org/project/moveq/)
[![License](https://img.shields.io/pypi/l/moveq.svg)](LICENSE)

`moveq` turns raw service and demographic data — trips per area, population
counts, deprivation ranks — into standard inequality measures (Gini, Palma,
Wagstaff Concentration Index), a configurable composite accessibility score,
and a cross-country harmonization registry for extending methodologies without
silent omissions.

It is a library stack, not a hosted product:

- **Modular & lightweight**: installable Python packages with no framework lock-in.
- **Pure NumPy core**: zero required I/O or GIS dependencies (`moveq-core`).
- **Standardized CLI**: quick CSV-in, numbers-out command-line interface (`moveq-cli`).
- **Harmonization registry**: programmatic `same`/`replace`/`omit` contracts for cross-country studies (`moveq-catalogue`).

`moveq` computes what the data shows. It does not decide policy — you keep that
judgment; `moveq` owns the math and the trail of what was computed.

---

## Installation

Requires Python 3.10 or newer.

```bash
pip install moveq          # Python API (core + catalogue)
pip install moveq-cli      # also installs the `moveq` command
pip install "moveq[frames]"  # optional pandas helpers
```

PyPI projects: [`moveq`](https://pypi.org/project/moveq/),
[`moveq-core`](https://pypi.org/project/moveq-core/),
[`moveq-catalogue`](https://pypi.org/project/moveq-catalogue/),
[`moveq-cli`](https://pypi.org/project/moveq-cli/).

### From source (editable)

```bash
git clone https://github.com/SVamseekar/moveq.git
cd moveq
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -e "reference/python/moveq-core[frames,test]"
pip install -e "reference/python/moveq-catalogue[test]"
pip install -e "reference/python/moveq[test]"
pip install -e "reference/python/moveq-cli[test]"
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full development setup.

---

## Packages

| Package | What it is |
| --- | --- |
| [`moveq-core`](reference/python/moveq-core/) | Gini, Palma, Concentration Index, weighted composite scoring, vulnerability indexing |
| [`moveq-catalogue`](reference/python/moveq-catalogue/) | Same/replace/omit registry for cross-country section catalogues |
| [`moveq`](reference/python/moveq/) | Umbrella package re-exporting both |
| [`moveq-cli`](reference/python/moveq-cli/) | `moveq` command-line tool |

All four packages are versioned in lockstep and released from one Git tag.

---

## Documentation

- [**Overview & Architecture**](docs/index.md)
- [**Methodology & Mathematical Formulations**](docs/methodology.md) (Gini, Palma, Concentration Index, Composite Scoring)
- [**Getting Started & CLI Guide**](docs/getting_started.md)
- [**Cross-Country Catalogue Harmonization Guide**](docs/catalogue_guide.md)
- [**API Reference**](docs/api_reference.md)
- [**Website**](https://moveq.souravamseekar.com) — static files in [`website/`](website/); Vercel deploys `main` to production and pull requests to preview URLs
- [**Publishing to PyPI**](docs/publishing.md) (maintainers)
- [**Changelog**](CHANGELOG.md)

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

### Command-line interface

```bash
moveq gini examples/basic_equity/data.csv --value trips --weight population
moveq palma examples/basic_equity/data.csv --value trips --weight population
moveq ci examples/basic_equity/data.csv --value trips --rank deprivation_rank --weight population

moveq score --terms '{"coverage": 0.8, "evening": 0.5}' --weights '{"coverage": 0.6, "evening": 0.4}'

moveq catalogue validate country_catalogue.json
```

See [`examples/basic_equity/run.py`](examples/basic_equity/run.py) for a runnable end-to-end demo.

---

## Running tests

```bash
pytest -v
```

CI runs on Python 3.10–3.13 ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)).
Releases are published from [`.github/workflows/publish.yml`](.github/workflows/publish.yml)
via PyPI Trusted Publishing. There is no production PyPI token in this repository.

---

## What moveq is not

- **Not a data pipeline or ingestion framework** — bring your own arrays or CSVs.
- **Not a hosted dashboard or SaaS product**.
- **Not tied to any single country's data sources** — algorithms are country-agnostic; `moveq-catalogue` manages the parts that aren't.

---

## Relationship to Aequitas

[Aequitas](https://github.com/) (the multi-country bus × deprivation briefing platform) is `moveq`'s flagship consumer and the origin of this methodology — `moveq` is the extraction of Aequitas's equity math and cross-country harmonization pattern into a standalone, reusable open-source library suite.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please follow the
[Code of Conduct](CODE_OF_CONDUCT.md). Security reports go through
[SECURITY.md](SECURITY.md), not public issues.

---

## License

[BSD 3-Clause](LICENSE).
