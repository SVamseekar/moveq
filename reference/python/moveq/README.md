# moveq

Umbrella package: re-exports `moveq-core` (equity math, composite scoring)
and `moveq-catalogue` (cross-country harmonization) behind one import.

```python
from moveq import compute_gini, compute_score, Catalogue, SectionAction
```

Install just the pieces you need instead if you don't want the combined
dependency footprint — `moveq-core` and `moveq-catalogue` are standalone.
