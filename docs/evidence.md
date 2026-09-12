# Evidence layer

A distributional finding is only as good as its reproducibility. moveq records
what happened *inside* the calculation on `EquityResult`. The evidence layer
records everything *upstream* of the array: which claim is being made, where
the data came from, which contract decisions were taken, and whether the
number still matches.

This is **not** a complete evidence system until every published case has a
manifest, the validator, and a CI check. Today four cases are published;
twenty-seven gallery entries are registered but not yet built. One reproduced
case exists (O'Donnell et al. 2008, Table 8.1). T1.1 remains proposed.

## Claim ladder

Every case carries exactly one badge. The pre-ladder labels (reproduce /
extend / operationalise / audit) are withdrawn.

| Badge | Meaning |
| --- | --- |
| **reproduced** | Same source data and declared method; moveq matches the published result within a stated tolerance |
| **recomputed** | Source data available; moveq applies an independently implemented equivalent method |
| **extended** | moveq adds a weighted, gradient-based, temporal or scenario analysis the source did not report |
| **blocked** | The published claim cannot be independently verified (missing data, formula, or transformations). A feature, not a failure. |
| **demonstrated** | Synthetic or illustrative |
| **proposed** | Pipeline incomplete (licence, retrieval, or extract) |

Badges are immutable per case id. Promotion requires the underlying condition
to change **and** a `claim_history` entry (`from`, `to`, `date`, `reason`).
A case does not become reproduced because a later run happened to agree.

Reproduction still requires published per-unit values, a stated formula, and
obtainable data. External statistics libraries are not test oracles.

Python:

```python
from moveq import CLAIM_BADGES, PROMOTION_RULES
```

## Manifest schema

Published cases are [Frictionless Data Packages](https://specs.frictionlessdata.io/data-package/):
`datapackage.json` plus resources. RO-Crate-style provenance (DOI, retrieval
date, licence, SHA-256) lives on `sources` and `resources[].hash`
(`sha256:<hex>`). The moveq contract is an additional `moveq` object — Data
Package explicitly allows extra properties.

`moveq.limitations` is required. The six contract decisions are always
present, and may be `null` when they do not apply:

| Decision | Where |
| --- | --- |
| Rank direction | `moveq.rank.direction` |
| Outcome kind | `moveq.outcome.kind` (`benefit` or `burden`) |
| Weights | `moveq.method.weight_kind` |
| Missing-data policy | `moveq.method.missing_policy` |
| CI variant | `moveq.method.variant` |
| Tolerance | `moveq.expected.tolerance` |

Blocked cases must not carry `expected.value` and must not declare a metric
to run. Demonstrated and reproduced cases require `expected.value`.

The YAML in [planning/04-evidence-layer.md](../planning/04-evidence-layer.md)
is the human illustration of these fields. JSON is the canonical form because
it is what Frictionless specifies and what the standard library can load
without a new dependency.

## Validator

```bash
moveq evidence validate examples/evidence
moveq evidence validate examples/evidence/t1.6-missing-term/datapackage.json --json
```

Checks, in order: schema, resource hashes, that the declared method is what
the library actually ran, and that the computed value lies within
`expected.tolerance`. Failure names the check. Non-zero exit.

In Python the same checks are in-memory (no filesystem):

```python
from moveq import validate_descriptor, sha256_bytes

report = validate_descriptor(descriptor, {"terms.json": payload})
if not report.ok:
    raise SystemExit(report.issues)
```

## Provenance on `EquityResult`

Additive, optional, default `None`:

- `source_id` — manifest `name`
- `software_version` — `moveq-core` version that produced the result (filled automatically)
- `data_hash` — SHA-256 of the input file, when the caller supplies it

They appear in `to_dict()`.

## Published cases

See [examples/evidence/](../examples/evidence/).

| Case | Badge | Notes |
| --- | --- | --- |
| O'Donnell 2008 Table 8.1 | reproduced | India U5MR by wealth quintile; published CI **−0.1694**. Extract is CC BY 3.0 IGO. Independent grouped-rank oracle agrees to 4 d.p. |
| T1.6 missing-term score | demonstrated | Oracle `composite_score` → 73.333… under `reweight`; `as_zero` is 55.0 |
| T1.7 nursing workforce | blocked | No country table; incomplete stated formula; data on request |
| T1.1 greenspace | proposed | Deposit is CC BY-NC 4.0; cannot be committed to a BSD-3-Clause repo |

T1.1 is still a reproduced *candidate* and is not reproduced. The O'Donnell
table is a different source: five published rows, a stated formula, and a
redistribution-compatible licence. Do not re-badge T1.1.

`CITATION.cff` is already at the repository root. Zenodo DOIs are a later,
separate decision.
