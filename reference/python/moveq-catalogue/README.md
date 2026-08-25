# moveq-catalogue

**Same / replace / omit registry for cross-country transport-equity
questionnaires.**

[![PyPI](https://img.shields.io/pypi/v/moveq-catalogue.svg)](https://pypi.org/project/moveq-catalogue/)
[![Python versions](https://img.shields.io/pypi/pyversions/moveq-catalogue.svg)](https://pypi.org/project/moveq-catalogue/)
[![License](https://img.shields.io/pypi/l/moveq-catalogue.svg)](https://github.com/SVamseekar/moveq/blob/main/LICENSE)

When a method built for one country (a coverage question, a deprivation
proxy, a night-service indicator) is reused in another, three things
happen in practice:

1. some items **transfer** — the question is the same; only the local
   dataset changes (GTFS here, a national timetable there)
2. some items **do not transfer** — the UK IMD is not the French *grille
   de densité*; you need a named local substitute
3. some items **cannot be measured** at small-area resolution in the
   destination country, and should be dropped *on the record*

Without an explicit contract, the usual failure is **silent omission**:
a base section is forgotten, inherited, or deleted in a spreadsheet, and
the two countries are compared as if they answered the same
questionnaire.

`moveq-catalogue` makes that contract programmatic. You list the **base
sections** once. For a target country you must `register` each section
as `SAME`, `REPLACE`, or `OMIT`. `validate()` returns leftover section
ids; an empty list means every base item has been decided. There is no
default. Forgetting is an error, not a zero.

This package has **no numeric dependency** (no NumPy). Most applications
should install [`moveq`](https://pypi.org/project/moveq/), which
re-exports `Catalogue` and `SectionAction`.

## The three actions

| Action | Meaning | What you must supply |
| --- | --- | --- |
| `SAME` | The question / method carries over against local data | Optional `note` (local source, geography) |
| `REPLACE` | A locally meaningful question takes its place | **Required** `replacement_title`; optional `note` |
| `OMIT` | No acceptable small-area variable exists | **Required** `note` explaining the drop |

`REPLACE` without a title, or `OMIT` without a note, raises. Registering
an unknown section id also raises. Duplicate ids in the base list are
rejected at construction.

`summary()` counts how many sections landed in each bucket, which is
useful in a methods appendix (“12 same, 3 replaced, 1 omitted”).

The full taxonomy and a worked multi-country example:
[catalogue guide](https://github.com/SVamseekar/moveq/blob/main/docs/catalogue_guide.md).

## Installation

Requires Python 3.10+.

```bash
pip install moveq-catalogue
```

## Usage

```python
from moveq_catalogue import Catalogue, SectionAction

base_sections = ["coverage_pct", "service_deserts", "policy_scenarios"]

ie = Catalogue(base_sections, country="ireland")
ie.register("coverage_pct", SectionAction.SAME, note="TFI × CSO Small Area")
ie.register("service_deserts", SectionAction.SAME)
ie.register(
    "policy_scenarios",
    SectionAction.REPLACE,
    replacement_title="Connecting Ireland / Local Link / BusConnects",
)

issues = ie.validate()
if issues:
    raise SystemExit(issues)  # e.g. a base section with no decision
print(ie.summary())  # {'same': 2, 'replace': 1, 'omit': 0}
```

## Documentation

- [Catalogue harmonization guide](https://github.com/SVamseekar/moveq/blob/main/docs/catalogue_guide.md)
- [API reference](https://github.com/SVamseekar/moveq/blob/main/docs/api_reference.md)
- [Umbrella package](https://pypi.org/project/moveq/)
- [Source](https://github.com/SVamseekar/moveq)
- [Changelog](https://github.com/SVamseekar/moveq/blob/main/CHANGELOG.md)

## License

[BSD 3-Clause](https://github.com/SVamseekar/moveq/blob/main/LICENSE).
