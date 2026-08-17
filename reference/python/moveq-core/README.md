# moveq-core

Pure algorithms for measuring transport equity:
- **Population-weighted Gini coefficient** via numerical Lorenz curve integration
- **Palma ratio** (top 10% highest-service vs bottom 40% lowest-service population)
- **Wagstaff Concentration Index** via fractional rank weighted covariance
- **Configurable weighted composite scoring** with dynamic missing-term renormalization

No I/O, no database or framework dependencies — feed it NumPy arrays, get numbers back.

---

## Quickstart

```python
import numpy as np
from moveq_core import (
    compute_gini,
    compute_palma_ratio,
    compute_concentration_index,
    compute_score,
)

service = np.array([10.0, 20.0, 5.0, 50.0, 8.0])
population = np.array([1000, 800, 1200, 300, 900])
deprivation_rank = np.array([1, 3, 2, 5, 4])  # 1 = most deprived

gini = compute_gini(service, population)
palma = compute_palma_ratio(service, population)
ci = compute_concentration_index(service, deprivation_rank, population)

# Composite score with graceful missing data handling
score_res = compute_score(
    terms={"coverage": 0.75, "evening": 0.50, "night": None},
    weights={"coverage": 0.50, "evening": 0.30, "night": 0.20},
)
print(f"Score: {score_res.score:.1f} ({score_res.note})")
```

---

## DataFrame Helpers (`moveq_core.frames`)

DataFrame helpers for multidimensional vulnerability indices and multi-factor deprivation flagging live in `moveq_core.frames` and require the `frames` extra:

```bash
pip install "moveq-core[frames]"
```

```python
import pandas as pd
from moveq_core.frames import compute_vulnerability_index, identify_multiply_deprived

df = pd.DataFrame({
    "unemployment_pct": [5.0, 12.0, 20.0],
    "no_car_pct": [10.0, 30.0, 60.0],
    "elderly_pct": [15.0, 25.0, 35.0],
})

vulnerability = compute_vulnerability_index(df, ["unemployment_pct", "no_car_pct", "elderly_pct"])
flagged = identify_multiply_deprived(df, ["unemployment_pct", "no_car_pct", "elderly_pct"], min_factors=2)
```

---

## Documentation

See the root documentation for detailed explanations and formal mathematical proofs:
- [Methodology & Mathematical Formulations](../../../docs/methodology.md)
- [API Reference](../../../docs/api_reference.md)
