# moveq-catalogue

Registry for the **same / replace / omit** pattern used to extend one country's
section questionnaire to another country without silent omissions.

[![PyPI](https://img.shields.io/pypi/v/moveq-catalogue.svg)](https://pypi.org/project/moveq-catalogue/)
[![Python versions](https://img.shields.io/pypi/pyversions/moveq-catalogue.svg)](https://pypi.org/project/moveq-catalogue/)
[![License](https://img.shields.io/pypi/l/moveq-catalogue.svg)](https://github.com/SVamseekar/moveq/blob/main/LICENSE)

- **same** — the question carries over; only the local data source changes
- **replace** — the question does not transfer; a locally meaningful replacement is required
- **omit** — no small-area variable exists; the section is dropped with a note

Most applications should install the umbrella package instead:

```bash
pip install moveq
```

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
ie.register("coverage_pct", SectionAction.SAME, note="TFI x CSO Small Area")
ie.register("service_deserts", SectionAction.SAME)
ie.register(
    "policy_scenarios",
    SectionAction.REPLACE,
    replacement_title="Connecting Ireland / Local Link / BusConnects",
)

assert ie.validate() == []  # every base section has been decided
print(ie.summary())  # {'same': 2, 'replace': 1, 'omit': 0}
```

`validate()` is the whole point of this package: it fails if a new country
silently forgets to decide what happens to a base section.

## Documentation

- [Catalogue harmonization guide](https://github.com/SVamseekar/moveq/blob/main/docs/catalogue_guide.md)
- [API reference](https://github.com/SVamseekar/moveq/blob/main/docs/api_reference.md)
- [Source repository](https://github.com/SVamseekar/moveq)
- [Changelog](https://github.com/SVamseekar/moveq/blob/main/CHANGELOG.md)

## License

[BSD 3-Clause](https://github.com/SVamseekar/moveq/blob/main/LICENSE).
