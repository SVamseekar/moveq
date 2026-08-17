# moveq-catalogue

Registry for the **same / replace / omit** pattern used to extend one country's section questionnaire or indicator framework to another country without silent omissions or methodological drift:

- **same** — exact same question carried over; local data source substituted underneath.
- **replace** — question doesn't transfer directly; a new, locally-meaningful question takes its place (requires replacement title).
- **omit** — no small-area variable exists; the section is explicitly dropped with an explanatory note.

---

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

`validate()` catches the failure mode this pattern exists to prevent: silently forgetting to decide what a new country does with a section from the base questionnaire.

---

## Documentation

See the root documentation for the full taxonomy guide:
- [Cross-Country Catalogue Harmonization Guide](../../../docs/catalogue_guide.md)
- [API Reference](../../../docs/api_reference.md)
