# moveq-core

Pure algorithms for measuring transport equity: population-weighted Gini,
Palma ratio, Wagstaff Concentration Index, and a configurable weighted
composite score. No I/O, no country-specific assumptions — feed it arrays,
get numbers back.

```python
import numpy as np
from moveq_core import compute_gini, compute_palma_ratio, compute_concentration_index

service = np.array([10, 20, 5, 50, 8])
population = np.array([1000, 800, 1200, 300, 900])
deprivation_rank = np.array([1, 3, 2, 5, 4])  # 1 = most deprived

gini = compute_gini(service, population)
palma = compute_palma_ratio(service, population)
ci = compute_concentration_index(service, deprivation_rank, population)
```

DataFrame convenience helpers (vulnerability index, triple-deprivation
flagging) live in `moveq_core.frames` and require the `frames` extra:

```bash
pip install "moveq-core[frames]"
```
