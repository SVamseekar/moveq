# moveq

**Python libraries for transport-equity analysis.**

moveq turns raw service and demographic data — trips per area, population,
a deprivation rank — into standard inequality measures (Gini, Palma,
Concentration Index), a configurable composite accessibility score, and a
registry for extending one country's methodology to another without
silently dropping questions along the way.

It is a library stack, not a hosted product:

- installable Python packages, no framework lock-in
- a small CLI for quick CSV-in, numbers-out use
- pure numpy core with zero required I/O dependencies

moveq computes what the data shows. It does not decide policy — you keep
that judgment; moveq owns the math and the trail of what was computed.

---

## Why moveq exists

Every transport-equity project reinvents the same handful of measures
(Gini, Palma, a concentration index) and then reinvents the same headache
when it tries to extend a single-country methodology to a second country:
which questions carry over unchanged, which need a locally-meaningful
replacement, and which have to be honestly omitted because the data
doesn't exist yet. That decision gets made once, informally, and is easy to
lose track of as a project grows to a third or fourth country.

moveq makes both problems programmatic:

1. **moveq-core** computes the inequality measures and a composite score
   from arrays you already have — no schema, no ORM, no coupling to any
   particular data source.
2. **moveq-catalogue** tracks the same/replace/omit decision per question
   per country, and refuses to let a question go undecided.

## Packages

| Package | What it is |
| --- | --- |
| [`moveq-core`](reference/python/moveq-core/) | Gini, Palma, Concentration Index, weighted composite scoring |
| [`moveq-catalogue`](reference/python/moveq-catalogue/) | Same/replace/omit registry for cross-country section catalogues |
| [`moveq`](reference/python/moveq/) | Umbrella package re-exporting both |
| [`moveq-cli`](reference/python/moveq-cli/) | `moveq` command-line tool |

## Install (from source)

```bash
git clone <this-repo>
cd moveq
python -m venv .venv
source .venv/bin/activate

pip install -e reference/python/moveq-core
pip install -e reference/python/moveq-catalogue
pip install -e reference/python/moveq
pip install -e reference/python/moveq-cli
```

## Quickstart

```python
import numpy as np
from moveq import compute_gini, compute_palma_ratio, compute_concentration_index, compute_score

service = np.array([10, 20, 5, 50, 8])
population = np.array([1000, 800, 1200, 300, 900])
deprivation_rank = np.array([1, 3, 2, 5, 4])

gini = compute_gini(service, population)
palma = compute_palma_ratio(service, population)
ci = compute_concentration_index(service, deprivation_rank, population)

result = compute_score(
    terms={"coverage": 0.7, "evening": 0.5, "frequency": None, "gap": 0.9},
    weights={"coverage": 0.40, "evening": 0.25, "frequency": 0.20, "gap": 0.15},
)
print(result.to_dict())
```

```bash
moveq gini examples/basic_equity/data.csv --value trips --weight population
```

See `examples/basic_equity/run.py` for a runnable end-to-end demo, including
the catalogue registry.

## What moveq is not

- Not a data pipeline, warehouse, or ingestion framework — bring your own
  arrays/CSV
- Not a hosted dashboard or SaaS product
- Not tied to any single country's data sources — the algorithms are
  country-agnostic; `moveq-catalogue` exists precisely to manage the parts
  that aren't

## Relationship to Aequitas

[Aequitas](https://github.com/) (the multi-country bus × deprivation
briefing platform) is moveq's flagship consumer and the origin of this
methodology — moveq is the extraction of Aequitas's equity math and
cross-country harmonization pattern into a standalone, reusable library
suite. Aequitas itself remains a separate, proprietary product built on top
of moveq.

## License

[BSD 3-Clause](LICENSE).
