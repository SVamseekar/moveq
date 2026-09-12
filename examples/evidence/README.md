# Evidence cases

Machine-readable gallery cases. Each published case is a [Frictionless Data Package](https://specs.frictionlessdata.io/data-package/) (`datapackage.json`) with a `moveq` contract block. The six-badge claim ladder and the schema live in `moveq_core.evidence`.

```bash
moveq evidence validate examples/evidence
```

CI runs the same command. A case that stops matching `expected` fails the build.

## Claim ladder

| Badge | Meaning |
| --- | --- |
| **reproduced** | Same source data and declared method; moveq matches the published result within `expected.tolerance` |
| **recomputed** | Source data available; moveq applies an independently implemented equivalent method |
| **extended** | moveq adds an analysis the source did not report |
| **blocked** | The published claim cannot be independently verified |
| **demonstrated** | Synthetic or illustrative |
| **proposed** | Pipeline incomplete (licence, retrieval, or extract) |

Exactly one badge per case. Promotion is recorded in `moveq.claim_history`; a case does not quietly become reproduced because a later run agreed.

`limitations` is required. The six contract decisions — rank direction, outcome kind, weight kind, missing-data policy, CI variant, and tolerance — are present on every descriptor even when the value is `null`.

## Published in this directory

| id | Badge | Why this badge |
| --- | --- | --- |
| `t1.6-missing-term` | demonstrated | Constructed 73.33 vs 55.00 missing-term swing; not a named region |
| `t1.7-nursing-workforce` | blocked | No country table; incomplete stated formula; data on request |
| `t1.1-greenspace` | proposed | City extract is CC BY-NC 4.0 and cannot be committed here |

`registry.json` lists all 30 gallery entries from `planning/07-gallery.md`. Unpublished rows have `"published": false` and no folder yet.

## What is not here

There is currently **no reproduced case**. T1.1 is the only candidate; the deposit licence blocks committing the per-city extract. Do not describe this directory as a complete evidence system.

Expected values for demonstrated cases come from the independent oracles in `reference/python/moveq-core/tests/oracles.py`, not from calling the production function once and pasting the output.
