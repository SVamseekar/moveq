# moveq Documentation

**`moveq`** is a Python library suite for transport-equity, spatial accessibility, and socio-spatial inequality analysis.

---

## What is `moveq`?

Every transport planning and transit accessibility analysis project encounters two core challenges:

1. **Computing Standard Inequality Metrics**: Calculating population-weighted distributional measures (such as the Gini coefficient, the Palma ratio, and the Wagstaff Concentration Index) and aggregating disparate indicators into composite scores without arbitrary ad-hoc scripts.
2. **Cross-Country Harmonization**: Adapting indicator frameworks and questionnaires across different countries without accidentally assuming identical data availability or silently dropping key equity dimensions.

`moveq` provides a lightweight, modular, pure NumPy/Python foundation for these tasks.

---

## Core Principles

- **Separation of Policy & Computation**: `moveq` computes what the data shows; policy judgment and normative decisions remain with the analyst.
- **Zero I/O Lock-in**: The core algorithms take plain NumPy arrays or dictionaries. No forced databases, heavy GIS frameworks, or cloud dependencies.
- **Graceful Missing Data Handling**: Missing indicators in composite scores are explicitly dropped and remaining weights are renormalized with explanatory metadata, rather than silently treated as zeros.
- **Strict Harmonization Contracts**: When expanding a study across jurisdictions, every section must be explicitly mapped (`SAME`, `REPLACE`, `OMIT`), guaranteeing methodological transparency.

---

## Package Architecture

```
moveq/
├── moveq-core/        # Pure NumPy equity algorithms and composite scoring
├── moveq-catalogue/   # Same/replace/omit cross-country harmonization registry
├── moveq/             # Top-level umbrella package
└── moveq-cli/         # CLI tool for CSV & JSON workflows
```

---

## Install

```bash
pip install moveq        # Python API
pip install moveq-cli    # also installs the `moveq` command
```

Source: <https://github.com/SVamseekar/moveq>.
PyPI: <https://pypi.org/project/moveq/>.

## Documentation Navigation

- [**Getting Started**](getting_started.md): Installation, quickstart recipes, and CLI guide.
- [**Methodology Guide**](methodology.md): Mathematical formulations of Gini, Palma, Concentration Index, and scoring algorithms.
- [**Catalogue Harmonization Guide**](catalogue_guide.md): The `SAME` / `REPLACE` / `OMIT` decision framework for international studies.
- [**API Reference**](api_reference.md): Complete module, class, and function documentation.
- [**Publishing to PyPI**](publishing.md): Maintainer runbook for versioning, Trusted Publishing, and GitHub Releases.
- [**Changelog**](../CHANGELOG.md): User-facing history of each lockstep release.
