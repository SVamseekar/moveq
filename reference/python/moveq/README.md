# moveq

Umbrella package: re-exports `moveq-core` (equity math, composite scoring, vulnerability indexing) and `moveq-catalogue` (cross-country harmonization registry) behind a single top-level import.

---

## Usage

```python
from moveq import (
    compute_gini,
    compute_palma_ratio,
    compute_concentration_index,
    compute_score,
    Catalogue,
    SectionAction,
)
```

Install just the individual subpackages (`moveq-core` or `moveq-catalogue`) if you want a minimal dependency footprint, or use `moveq` as the single dependency for your project.

---

## Documentation

See the root documentation for comprehensive guides and API references:
- [Overview & Architecture](../../../docs/index.md)
- [Methodology & Mathematical Formulations](../../../docs/methodology.md)
- [Getting Started Guide](../../../docs/getting_started.md)
- [Catalogue Harmonization Guide](../../../docs/catalogue_guide.md)
- [API Reference](../../../docs/api_reference.md)
