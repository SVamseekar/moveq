# moveq-catalogue

Registry for the **same / replace / omit** pattern used to extend one
country's section questionnaire to another country without renaming pages
or forcing a copy of every card:

- **same** — same question, local data source substituted underneath
- **replace** — the question doesn't transfer; a new, locally-meaningful
  question takes its place
- **omit** — no free small-area variable exists yet; the section is dropped
  with a one-line reason, not silently hidden

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

`validate()` catches the failure mode this pattern exists to prevent:
silently forgetting to decide what a new country does with a section from
the base questionnaire.
