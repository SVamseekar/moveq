# moveq

**Transport-equity analysis for Python.**

[![PyPI](https://img.shields.io/pypi/v/moveq.svg)](https://pypi.org/project/moveq/)
[![Python versions](https://img.shields.io/pypi/pyversions/moveq.svg)](https://pypi.org/project/moveq/)
[![License](https://img.shields.io/pypi/l/moveq.svg)](https://github.com/SVamseekar/moveq/blob/main/LICENSE)

`moveq` is the umbrella package for the moveq stack. It re-exports
[`moveq-core`](https://pypi.org/project/moveq-core/) (Gini, Palma, Concentration
Index, composite scoring) and
[`moveq-catalogue`](https://pypi.org/project/moveq-catalogue/) (cross-country
`same` / `replace` / `omit` registry) behind a single import.

Install this package unless you specifically want a slimmer dependency tree.

## Installation

Requires Python 3.10+.

```bash
pip install moveq
```

Pandas DataFrame helpers (vulnerability indexing):

```bash
pip install "moveq[frames]"
```

Command-line interface:

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
print(result.score, result.note)
```

`moveq` computes what the data shows. It does not decide policy.

## Related packages

| Package | Role |
| --- | --- |
| [`moveq`](https://pypi.org/project/moveq/) | Umbrella import (this package) |
| [`moveq-core`](https://pypi.org/project/moveq-core/) | Pure NumPy algorithms |
| [`moveq-catalogue`](https://pypi.org/project/moveq-catalogue/) | Harmonization registry |
| [`moveq-cli`](https://pypi.org/project/moveq-cli/) | `moveq` command-line tool |

## Documentation

Source, issues, and the full guides live on GitHub:

- [Overview](https://github.com/SVamseekar/moveq/blob/main/docs/index.md)
- [Getting started](https://github.com/SVamseekar/moveq/blob/main/docs/getting_started.md)
- [Methodology](https://github.com/SVamseekar/moveq/blob/main/docs/methodology.md)
- [Catalogue guide](https://github.com/SVamseekar/moveq/blob/main/docs/catalogue_guide.md)
- [API reference](https://github.com/SVamseekar/moveq/blob/main/docs/api_reference.md)
- [Changelog](https://github.com/SVamseekar/moveq/blob/main/CHANGELOG.md)

## License

[BSD 3-Clause](https://github.com/SVamseekar/moveq/blob/main/LICENSE).
