# moveq

**Transport-equity analysis for Python.**

[![PyPI](https://img.shields.io/pypi/v/moveq.svg)](https://pypi.org/project/moveq/)
[![Python versions](https://img.shields.io/pypi/pyversions/moveq.svg)](https://pypi.org/project/moveq/)
[![License](https://img.shields.io/pypi/l/moveq.svg)](https://github.com/SVamseekar/moveq/blob/main/LICENSE)

`moveq` turns the numbers you already have — trips per area, population
counts, deprivation ranks, coverage shares — into **standard inequality
measures** and a **documented composite accessibility score**, plus a
**cross-country catalogue contract** so a study cannot silently drop a
section when it moves from one country to another.

It is a library stack, not a hosted product. You bring arrays or CSVs;
`moveq` owns the math and the trail of what was computed. It does **not**
decide policy.

This package is the one most people should install. It re-exports the
public API of [`moveq-core`](https://pypi.org/project/moveq-core/) and
[`moveq-catalogue`](https://pypi.org/project/moveq-catalogue/) behind
`import moveq`. The command-line tool is a separate install:
[`moveq-cli`](https://pypi.org/project/moveq-cli/).

## What it computes

**Inequality of service (who gets how much).** Given a service value per
area (weekly trips, departures, coverage) and a population weight:

- **Gini** — overall inequality of that service across people. `0` is
  equal service for everyone; values toward `1` mean service is
  concentrated on a small share of the population. Internally this is a
  population-weighted Lorenz curve, integrated with the trapezoid rule.
- **Palma ratio** — the *extremes*: mean service of the best-served 10%
  of the population divided by mean service of the worst-served 40%.
  Equal service yields `1`. If the bottom 40% have no service at all, the
  result is infinity.

Neither Gini nor Palma knows anything about income or deprivation. They
only describe the distribution of the service variable.

**Inequality *along* deprivation (who is favoured).** The **Wagstaff
Concentration Index** ranks areas by a socioeconomic variable (for
example Index of Multiple Deprivation, where `1` is most deprived) and
asks whether service rises or falls along that ranking. The index lies
in `[-1, 1]`:

- **positive** — service is concentrated among *less* deprived areas
  (pro-rich)
- **negative** — service is concentrated among *more* deprived areas
  (pro-poor)
- **zero** — no systematic gradient with rank

**A composite score that does not treat missing data as zero.** Accessibility
work almost always has holes: night frequency was not collected, weekend
service is unknown for one cut. `compute_score` takes named terms in
`[0, 1]` and design weights. Any term that is `None` is **dropped** and
the remaining weights are **renormalised**. The result is a 0–100 score
plus a component table (`design_weight` vs `weight_used`, which terms
were dropped, and a human-readable `note`). If every term is missing,
the score is `None` rather than a silent `0`.

**A same / replace / omit registry for multi-country work.** When a
questionnaire or indicator list is reused in a second country, some
items map cleanly, some need a local substitute, and some cannot be
measured at small-area resolution. [`Catalogue`](https://pypi.org/project/moveq-catalogue/)
requires an explicit decision for *every* base section so an item cannot
disappear without a record.

The [methodology guide](https://github.com/SVamseekar/moveq/blob/main/docs/methodology.md)
has the formulae.

## Installation

Requires Python 3.10+.

```bash
pip install moveq
```

Pandas helpers for a vulnerability index and “multiply deprived” flags:

```bash
pip install "moveq[frames]"
```

CSV / JSON command line (installs this package as a dependency):

```bash
pip install moveq-cli
```

## Quickstart

```python
import numpy as np
from moveq import (
    compute_gini,
    compute_palma_ratio,
    compute_concentration_index,
    compute_score,
    Catalogue,
    SectionAction,
)

service = np.array([10.0, 20.0, 5.0, 50.0, 8.0])
population = np.array([1000, 800, 1200, 300, 900])
deprivation_rank = np.array([1, 3, 2, 5, 4])  # 1 = most deprived

gini = compute_gini(service, population)
palma = compute_palma_ratio(service, population)
ci = compute_concentration_index(service, deprivation_rank, population)

result = compute_score(
    terms={"coverage": 0.7, "evening": 0.5, "frequency": None, "gap": 0.9},
    weights={"coverage": 0.40, "evening": 0.25, "frequency": 0.20, "gap": 0.15},
)
# result.score is on 0–100; result.dropped lists terms that were None
```

## Package layout

| PyPI project | Role |
| --- | --- |
| **`moveq`** (this package) | Single import for the Python API |
| [`moveq-core`](https://pypi.org/project/moveq-core/) | NumPy algorithms; optional pandas extras |
| [`moveq-catalogue`](https://pypi.org/project/moveq-catalogue/) | Harmonization registry |
| [`moveq-cli`](https://pypi.org/project/moveq-cli/) | `moveq` command for CSV and JSON |

All four are versioned together.

## What this stack is not

- Not a GIS toolkit, GTFS parser, or data pipeline — pass in arrays or CSVs.
- Not a dashboard or SaaS product.
- Not a legal or policy verdict. Rankings and cut-offs stay with the analyst.

## Documentation

- [Overview](https://github.com/SVamseekar/moveq/blob/main/docs/index.md)
- [Getting started](https://github.com/SVamseekar/moveq/blob/main/docs/getting_started.md)
- [Methodology](https://github.com/SVamseekar/moveq/blob/main/docs/methodology.md)
- [Catalogue guide](https://github.com/SVamseekar/moveq/blob/main/docs/catalogue_guide.md)
- [API reference](https://github.com/SVamseekar/moveq/blob/main/docs/api_reference.md)
- [Changelog](https://github.com/SVamseekar/moveq/blob/main/CHANGELOG.md)
- [Source](https://github.com/SVamseekar/moveq)

## License

[BSD 3-Clause](https://github.com/SVamseekar/moveq/blob/main/LICENSE).
