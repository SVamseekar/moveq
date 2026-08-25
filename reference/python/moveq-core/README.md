# moveq-core

**Pure NumPy algorithms for measuring transport equity.**

[![PyPI](https://img.shields.io/pypi/v/moveq-core.svg)](https://pypi.org/project/moveq-core/)
[![Python versions](https://img.shields.io/pypi/pyversions/moveq-core.svg)](https://pypi.org/project/moveq-core/)
[![License](https://img.shields.io/pypi/l/moveq-core.svg)](https://github.com/SVamseekar/moveq/blob/main/LICENSE)

This is the calculation engine of the [moveq](https://pypi.org/project/moveq/)
stack. It has **no I/O**: you pass NumPy arrays (or, with the optional
`frames` extra, a pandas DataFrame) and get numbers and small result objects
back. There is no database, GIS library, or network client.

Most applications should install the umbrella package
[`moveq`](https://pypi.org/project/moveq/), which re-exports this API.
Install `moveq-core` directly only when you want the metrics without the
catalogue registry.

## What each metric is for

Transport analysis usually has a **service** variable per area (trips,
departures, coverage) and a **population** weight. Sometimes there is also a
**socioeconomic rank** (deprivation index, income band).

### Population-weighted Gini

Gini answers: *how unevenly is this service spread across people?*

Areas are sorted from lowest to highest service. Cumulative population share
is plotted against cumulative service share (a Lorenz curve). Gini is `1`
minus twice the area under that curve, using trapezoidal integration.

- `0` — every person faces the same service level (including the all-zero
  convention: nothing to distribute)
- toward `1` — almost all service sits with a small share of the population

Gini does **not** know whether the poorly served people are deprived. It is
a statement about the service distribution only.

### Palma ratio

Palma answers: *how does the best-served tenth compare with the worst-served
two-fifths?*

It is the population-weighted mean service of the top 10% divided by that of
the bottom 40% (areas on the boundary of those shares are split
proportionally). Equal service, including all-zero service, gives `1`. If
the bottom 40% have zero service while the top 10% do not, the function
returns `inf` rather than dividing by zero.

Palma is more sensitive to the tails than Gini, which is why the two are
reported together.

### Wagstaff Concentration Index

The concentration index answers: *does service rise or fall as deprivation
falls?*

Areas are ordered by rank (`1` = most deprived by convention in this
library). Units that tie on rank share the group's midpoint fractional
rank, so the answer does not depend on input order. Unpopulated units are
ignored. A population-weighted covariance between service and fractional
rank is scaled by the mean service. For non-negative service the result is
in `[-1, 1]`:

| Sign | Meaning |
| --- | --- |
| `CI > 0` | service concentrated in **less** deprived areas (pro-rich) |
| `CI < 0` | service concentrated in **more** deprived areas (pro-poor) |
| `CI = 0` | no systematic gradient with rank |

This is the metric to use when the policy question is about *socioeconomic
targeting*, not only about overall unevenness.

### Composite score with missing-term renormalisation

`compute_score` builds a 0–100 weighted index from named terms in `[0, 1]`.
The important behaviour is what happens when a term is `None`:

1. that term is **dropped**, not treated as zero
2. remaining design weights are **renormalised** to sum to 1
3. the result records `weight_used` vs `design_weight`, the dropped ids,
   and a `note`

If every term is missing, `score` is `None`. Design weights must be finite
and strictly positive; non-finite term values are rejected rather than
clipped. Callers keep control of which indicators exist; the library
refuses to invent a zero.

### Optional DataFrame helpers (`moveq_core.frames`)

With `pip install "moveq-core[frames]"` (or `"moveq[frames]"`):

- **vulnerability index** — min-max scale several deprivation-like columns
  to 0–100 and take the row-wise mean
- **multiply deprived** — flag areas that sit in the worst tertile on at
  least *k* factors at once

These are convenience summaries, not a substitute for a national IMD.

Formulae: [methodology](https://github.com/SVamseekar/moveq/blob/main/docs/methodology.md).

## Installation

Requires Python 3.10+. Runtime dependency: `numpy>=1.24`.

```bash
pip install moveq-core
pip install "moveq-core[frames]"   # pandas helpers
```

## Quickstart

```python
import numpy as np
from moveq_core import (
    compute_gini,
    compute_palma_ratio,
    compute_concentration_index,
    gini_result,
    compute_score,
)

service = np.array([10.0, 20.0, 5.0, 50.0, 8.0])
population = np.array([1000, 800, 1200, 300, 900])
deprivation_rank = np.array([1, 3, 2, 5, 4])  # 1 = most deprived

gini = compute_gini(service, population)
palma = compute_palma_ratio(service, population)
ci = compute_concentration_index(service, deprivation_rank, population)
gini_audit = gini_result(service, population)  # EquityResult: value, method, n_areas, …

score_res = compute_score(
    terms={"coverage": 0.75, "evening": 0.50, "night": None},
    weights={"coverage": 0.50, "evening": 0.30, "night": 0.20},
)
print(score_res.score, score_res.dropped, score_res.note)
```

## Documentation

- [Methodology](https://github.com/SVamseekar/moveq/blob/main/docs/methodology.md)
- [API reference](https://github.com/SVamseekar/moveq/blob/main/docs/api_reference.md)
- [Umbrella package](https://pypi.org/project/moveq/)
- [Source](https://github.com/SVamseekar/moveq)
- [Changelog](https://github.com/SVamseekar/moveq/blob/main/CHANGELOG.md)

## License

[BSD 3-Clause](https://github.com/SVamseekar/moveq/blob/main/LICENSE).
