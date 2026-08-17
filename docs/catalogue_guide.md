# Cross-Country Catalogue Harmonization Guide

A core challenge in international transport equity research is transferring a methodology (e.g. accessibility scoring, deprivation metrics, frequency measures) developed for one country to others without introducing silent errors or invalid comparisons.

`moveq-catalogue` formalizes this decision-making process into an explicit programmatic contract.

---

## 1. The Multi-Country Problem

When a transport-equity briefing model is expanded from a base country (e.g. the UK) to a second or third country (e.g. France, Germany, or the US):
- Some data definitions map cleanly (e.g. GTFS timetable feeds).
- Other indicators need localized replacements (e.g. replacing the UK Index of Multiple Deprivation (IMD) with French INSEE *Grille communale de densité* or US census ACS median income).
- Some indicators simply do not exist at a small-area resolution in the destination country (e.g. lack of open spatial data for late-night frequency).

Without an explicit contract, projects often suffer from **methodological drift** — unconsidered base sections get silently inherited or omitted without documentation.

---

## 2. The SAME / REPLACE / OMIT Taxonomy

`moveq-catalogue` requires each section to have one of three explicit actions:

| Action | Meaning | Requirements |
| :--- | :--- | :--- |
| `SAME` | The exact question / methodology carries over against local data. | Optional `note` detailing local dataset source. |
| `REPLACE` | The base question is substituted with a locally-meaningful equivalent. | **Required** `replacement_title` and optional `note`. |
| `OMIT` | The question is explicitly dropped because data is not available. | **Required** `note` justifying why the section was omitted. |

---

## 3. Using the Python API

### Creating and Validating a Catalogue

```python
from moveq_catalogue import Catalogue, SectionAction

# 1. Define base questionnaire sections
base_sections = [
    "coverage_400m",
    "evening_service_gap",
    "social_housing_access",
    "night_bus_network",
]

# 2. Initialize catalogue for the target country
catalogue = Catalogue(base_sections, country="france")

# 3. Register decisions for each section
catalogue.register(
    "coverage_400m",
    SectionAction.SAME,
    note="Computed using National GTFS feed x IRIS census boundaries",
)

catalogue.register(
    "social_housing_access",
    SectionAction.REPLACE,
    replacement_title="Access to HLM (Habitation à Loyer Modéré) clusters",
    note="INSEE FiloSoFi housing register",
)

catalogue.register(
    "night_bus_network",
    SectionAction.OMIT,
    note="No standardized night transit schedule data in regional departments",
)

# 4. Validate catalogue completeness
issues = catalogue.validate()
if issues:
    print("Incomplete catalogue:", issues)
    # Output: ["france: 1 section(s) not mapped: evening_service_gap"]
else:
    print("Summary:", catalogue.summary())
```

---

## 4. Using the CLI Validator

You can define catalogue specifications in JSON format:

```json
{
  "country": "germany",
  "base_sections": [
    "coverage_400m",
    "frequency_peak",
    "deprivation_gap"
  ],
  "mappings": [
    {
      "section_id": "coverage_400m",
      "action": "same",
      "note": "DELFI national transit data"
    },
    {
      "section_id": "frequency_peak",
      "action": "same"
    },
    {
      "section_id": "deprivation_gap",
      "action": "replace",
      "replacement_title": "German Index of Socioeconomic Deprivation (GISD)",
      "note": "Robert Koch Institute GISD small-area indicators"
    }
  ]
}
```

Run validation from your terminal:

```bash
moveq catalogue validate germany_catalogue.json
```

Output:
```text
country: germany
summary: same=2, replace=1, omit=0
status: valid (fully specified)
```
