# moveq Example Gallery — Design

**Date:** 2026-09-05
**Status:** Design approved, pending implementation plan

---

## 1. Purpose

moveq has a user guide (`docs/`) and an API reference (`website/reference/`). It has
no middle layer: no place that shows the library applied to a real problem. That gap
is the main obstacle to adoption. Readers who do not already know what a Wagstaff
Concentration Index is have no route into the library.

The gallery fills that layer. It is modelled on the PyMC-Marketing example gallery:
a visual index of worked examples, grouped under headings, each card a thumbnail and
a title linking to a runnable example.

## 2. Organising principle

Entries are organised by **the decision being made**, not by domain and not by which
moveq function they exercise.

An earlier draft of this design organised 40 entries as "consumer 20 / academic 20".
That was wrong, for a reason worth recording: generating entries by asking "where
else can Gini apply?" produces many skins around one calculation. Six of that
draft's consumer entries were `compute_gini` over a small array with the noun
changed.

The correct generating question is:

> What do people, organisations and governments actually have to decide, where are
> they currently using an average, count, threshold or ratio, and what does the
> distribution underneath it show?

Every entry must name a decision that changes depending on how it is measured.

## 3. The argument

The research behind this design surfaced one consistent pattern across every domain
examined: **these are distributions being reported as scalars.**

- "9.2% of the EU cannot heat their home" — a mean across wildly unequal regions
- "Half of Wallonia's communes have a doctor shortage" — a threshold count that
  discards how far below the line each commune sits
- "Valletta 0.7 m² vs Vilnius 66.3 m² of green space per person" — a min/max ratio
  that says nothing about the other 24 capitals
- "97% of children are within acceptable distance of a school" — a count that hides
  who the 3% are
- "Average response time is 4 hours" — compatible with 80% of users waiting 30
  minutes and 20% waiting 18 hours

Each headline discards the shape of the thing being complained about. That is the
gallery's thesis and the library's value proposition, and it is evidenced rather
than asserted.

A secondary theme, recurring often enough to deserve its own section: **equal policy,
unequal consequence.** The same £200 allowance, the same two work-from-home days,
the same reimbursement rate — equal inputs producing unequal burdens.

## 4. Card schema

Every card carries the same four fields. No card ships without all four.

| Field | Content |
|---|---|
| **The real question** | The decision, in the words of the person making it |
| **Normally reported as** | The average, count, threshold or ratio currently used |
| **What moveq adds** | The metric, and what it reveals that the scalar hid |
| **What changed** | The concrete delta — who is affected differently, by how much |

Plus a **buildability status** (see §7) and, where the entry rests on published
work, a citation.

## 5. Sections and entries

### Section A — The average hides the distribution

Entries where a mean is reported and the spread is discarded.

| # | Entry | Decision | Components | Status |
|---|---|---|---|---|
| A1 | Same average, very different cities | Are these two cities equivalent? | gini | Synthetic |
| A2 | Emergency department access | Does "24 min average" describe everyone? | CI, frames | Buildable |
| A3 | Customer support wait times | Does "4 hour average" describe everyone? | gini | Synthetic |
| A4 | EU energy poverty × income | Is it concentrated among the poor, or just colder countries? | CI, cli, frames | Buildable |
| A5 | Green space across 26 capitals | What about the 24 cities the headline ignores? | gini, cli | Buildable |
| A6 | Air pollution × poverty | Who breathes the worst air? | CI, frames | Buildable |
| A7 | Childcare cost across the EU | Country-level means vs household burden | gini | Weak — country-level only |

A1 is the purest demonstration in the gallery: two constructed cities, identical mean
service, radically different distributions. A dashboard reports "10" for both. It
should be the first card.

### Section B — Equal rules, unequal outcomes

Entries where a uniform policy produces a non-uniform burden. This is the strongest
consumer-facing theme.

| # | Entry | Decision | Components | Status |
|---|---|---|---|---|
| B1 | Is hybrid work fair? | Same policy, different commutes and roles | gini, score, spread | Synthetic |
| B2 | What does commuting really cost employees? | Does the same salary mean the same burden? | score, spread | Synthetic |
| B3 | Who pays the real cost of an office relocation? | Which employee bears most of the move? | score, spread | Synthetic |
| B4 | Rent vs commute balancer | Should the long-commute flatmate pay less? | gini, score | Synthetic |
| B5 | Same commute allowance | £200 each, £40 to £190 actually spent | gini, spread | Synthetic |
| B6 | Same childcare benefit | Equal payment, unequal local costs | gini | Synthetic |
| B7 | Same remote-work policy | Equal days, unequal ability to use them | score, spread | Synthetic |
| B8 | Same parking policy | Equal access, unequal cost and time | score | Synthetic |
| B9 | Same travel reimbursement rate | Flat rate, unequal effective coverage | gini, spread | Synthetic |
| B10 | Who gets the worst hotel room? | Six friends, rooms differing on five axes | score | Synthetic |
| B11 | Who actually pays more for the wedding? | £500 each, plus travel, leave and unpaid hours | score, spread | Synthetic |
| B12 | Is household work actually shared equally? | Weighted by frequency, duration, inconvenience | gini, spread | Synthetic |
| B13 | Fair meeting point | Where do we meet, without stranding anyone? | gini, spread | Synthetic |
| B14 | Shift rota fairness | Who keeps getting the weekends? | gini, spread | Synthetic |
| B15 | On-call burden | Who carries the unsocial hours? | gini, spread | Synthetic |
| B16 | Group trip cost split | Weighted by room, nights, participation | score | Synthetic |

B12 is where `spread_result()` earns its existence: at n=4 the small-group measure is
the *only* honest anti-sacrifice metric, because Palma is undefined at that scale.
The example should say so explicitly.

### Section C — Counts and thresholds hide who is affected

Entries where an absolute number or a pass/fail rate is reported, and the identity of
the affected population is lost.

| # | Entry | Decision | Components | Status |
|---|---|---|---|---|
| C1 | Which neighbourhoods lost when pharmacies closed? | Before/after service concentration | CI, frames | Data-blocked |
| C2 | Who actually gets EV charging access? | 1,000 new points — for whom? | CI, frames | Buildable |
| C3 | School places: who are the 3%? | 97% within distance — and the rest? | CI | Buildable |
| C4 | Public library closures | Five closed — whose five? | CI | Data-blocked |
| C5 | ATM and cash access | 15,000 to 10,000 — evenly? | gini, cli | Buildable |
| C6 | Banking deserts in Spain | Branches down 50% — whose branches? | gini, CI, frames | Buildable |
| C7 | GP deserts in Wallonia | "Half of communes" — how far below the line? | gini, CI | Buildable |
| C8 | Dental access across 11 countries | 6% unmet need — concentrated where? | CI, catalogue | Buildable |
| C9 | SEND / EHC plan waits | "Massive variation" made numerical | gini, CI | Buildable |
| C10 | Continuing Healthcare by ICB | 2× variation at similar demographics | CI | Buildable |
| C11 | NHS waits by deprivation | Quintile tables to one signed number | CI, cli, frames | Buildable |
| C12 | 3-30-300 compliance | The distribution behind the pass rate | gini, frames | Buildable |
| C13 | Food bank / social support access | 40 centres — matched to need? | CI | Data-blocked |
| C14 | Rural transport isolation | Who is below the service floor? | gini, palma | Buildable |
| C15 | Regional poverty risk, NUTS2 | 25 regions above 33% — the shape below | gini, palma, cli | Buildable |
| C16 | 15-minute city | Within-city inequality, 100k+ cities | gini, frames | Buildable — replication |

C16 is a replication entry: the source study already publishes within-city inequality
figures, so reproducing them validates moveq against an independent result. That is
the strongest credibility mechanism available to a young library, and more such
entries should be sought.

### Section D — Interventions: did it reduce inequality, or raise the average?

Before/after entries. This section carries the library's sharpest argument.

| # | Entry | Decision | Components | Status |
|---|---|---|---|---|
| D1 | Did the intervention reduce inequality or just raise the mean? | The manifesto card | gini, CI | Synthetic |
| D2 | Where should the next bus go? | Two candidate areas, same population | gini, CI | Buildable |
| D3 | A bus route improved — who benefited? | Before/after, same population and ranks | gini, CI | Buildable |
| D4 | Who gained from the new rail station? | Did gains accrue to the already well-served? | CI, frames | Buildable |
| D5 | Which catchment gets the extra weekend clinic? | One session to allocate | CI | Buildable |

D1 should be constructed so that the average rises while the Concentration Index
worsens — the case that scalar reporting cannot distinguish and that policy
evaluation most needs to catch.

### Section E — Research and statutory measurement

Entries serving funded research and legal reporting obligations. This section carries
`moveq-catalogue` and most `moveq-cli` coverage.

| # | Entry | Decision | Components | Status |
|---|---|---|---|---|
| E1 | Social Climate Fund vulnerability | 27 states must measure energy and transport poverty | CI, score, catalogue | Buildable |
| E2 | Transport poverty composite | The EU legal definition is multi-dimensional | score, cli | Buildable |
| E3 | Harmonizing five deprivation indices | IMD, SEIFA, NZDep, ADI/SVI, EU-SILC | catalogue, CI | Buildable |
| E4 | Green space × income (JRC) | Signed magnitude, comparable across cities | CI, frames | Buildable |
| E5 | AURIN Australia × SEIFA | Spatial access with a national rank | CI, catalogue | Buildable |
| E6 | NZ Indigenous service access × NZDep | Access with a culturally-situated rank | CI, catalogue | Buildable |
| E7 | Same analysis from the command line | Any entry above, via CSV | cli | Buildable |
| E8 | Reading the audit trail | `n_dropped`, `warnings`, `note`, `context` | EquityResult | Buildable |

E1 is the single strongest institutional case in the gallery: the Social Climate Fund
is €86.7bn across 2026–2032, and all 27 member states are legally required to submit
Social Climate Plans measuring energy and transport poverty. It is a recurring,
funded, statutory measurement need.

E8 is the differentiator entry. R and Stata return a number; moveq returns a number
plus what it dropped and why. For any figure that must survive a reviewer, auditor or
regulator, that is the reason to choose this library.

## 6. Library coverage

| Component | Sections covering it |
|---|---|
| `compute_gini` / `gini_result` | A, B, C, D |
| `compute_score` | A, B, E |
| `compute_palma_ratio` / `palma_result` | C14, C15 (n≥200, well-posed) |
| `compute_concentration_index` | A, C, D, E |
| `spread_result()` (new) | B (small-n entries) |
| `EquityResult` audit fields | E8, and displayed throughout |
| `moveq` (re-export) | Every entry — the default import |
| `moveq-catalogue` | C8, E1, E3, E5, E6 |
| `moveq-cli` | A4, A5, C5, C15, E2, E7 |
| `moveq[frames]` | A2, A4, A6, C1, C2, C6, C11, C12, C16, D4, E4 |

Palma appears only where the unit count supports the 40/90 split. It is deliberately
absent from every small-group entry, and B12 states why.

## 7. Buildability status

Each entry carries one of three states, shown on the card:

- **Buildable** — real published data exists and has been located
- **Synthetic** — constructed inputs, honest and clearly labelled; appropriate for
  the consumer and demonstration entries, where the point is the method
- **Data-blocked** — the problem is real and evidenced, but per-area data could not be
  sourced. Listed as contribution-wanted rather than hidden.

Known data-blocked entries, all carried in the tables above: C1 pharmacy closures by
area (PGEU's evidence is qualitative), C4 library closures by community, and C13 food
bank capacity by area.

One further candidate — energy billing complaints by region — is not listed as an
entry at all. Only national totals are published (46,532 ombudsman cases in H1 2026),
with no regional breakdown found. It is recorded here so the omission is deliberate
rather than an oversight; if a regional source appears, it belongs in Section C.

Synthetic entries must never be presented as measurements of the real world. Each
states its inputs are constructed and what it is demonstrating.

## 8. Technical design

**Structure.** Each entry is a runnable `.py` under `examples/<section>/<entry>/`,
following the existing `examples/basic_equity/run.py` pattern. Each produces one
chart, which becomes its gallery thumbnail.

**Execution.** Examples run in CI. A broken example fails the build. This follows the
existing `scripts/check_website.py` discipline and prevents the documentation rot that
hand-written code samples suffer.

**Data.** Small committed CSV extracts with provenance notes, not live downloads. Live
fetching would make CI depend on external availability and licensing. Each dataset
carries its source URL, retrieval date and licence.

**Site.** Gallery index at `website/examples/`, between `guides/` and `reference/`.
Static HTML consistent with the existing site. Cards show thumbnail, title,
one-line description and buildability badge, grouped under the five section headings.
No filtering or search in the first version.

**New library code.** `spread_result()` in `moveq-core`, returning an `EquityResult`
with `metric="spread"`, following the existing `gini_result` / `palma_result`
pattern. It is the small-n counterpart to Palma: an anti-sacrifice measure that is
well-defined at n=4. It needs its own tests and a methodology section documenting
when to use it instead of Palma.

## 9. Delivery

The gallery ships incrementally. A card is published only when its example runs.

**First tranche — the argument in five cards:**

- A1 Same average, very different cities (the purest demonstration)
- D1 Did it reduce inequality or raise the mean? (the manifesto)
- B13 Fair meeting point (the consumer entry point)
- B4 Rent vs commute balancer (the most novel consumer case)
- E8 Reading the audit trail (the differentiator)

These five state the whole argument and exercise Gini, score, spread, CI and the
audit trail.

**Second tranche:** the buildable statutory and research entries — E1, E3, C11, A4,
C16 — which carry `catalogue`, `cli` and `frames`.

**Thereafter:** remaining buildable entries, then synthetic ones, with data-blocked
entries listed as open contributions throughout.

## 10. Risks

**Data acquisition dominates the buildable entries.** Fetching, cleaning and
licence-checking real data is most of the work; the moveq calls are a few lines.
Mitigated by committing small extracts rather than building an ingestion pipeline.
moveq is a library that takes arrays and CSVs — the gallery must not turn it into a
GIS or data platform.

**Synthetic entries risk reading as toys.** Mitigated by the card schema: naming a
real decision and a real reported scalar keeps the framing concrete even when the
numbers are constructed.

**`spread_result()` is new public API.** It needs tests, documentation and a clear
methodology note, and it commits the library to supporting a small-n path.

**The public "dumb pipes" claim needs correcting.** Existing meeting-point products
already minimise the longest journey; the differentiator is explaining and auditing
the result, not computing it. Any site copy asserting otherwise should be revised.

## 11. Sources

Statutory and policy:
- Social Climate Fund — https://eur-lex.europa.eu/EN/legal-content/summary/social-climate-fund.html
- EU transport poverty definition — https://cer.be/images/publications/facts-figures/250602_CER_Factsheet_Transport_poverty.pdf
- Energy Poverty Advisory Hub indicators — https://energy-poverty.ec.europa.eu/epah-indicators

Research and data:
- 15-minute city accessibility inequality — https://www.nature.com/articles/s42949-023-00133-w
- 3-30-300 assessment of European cities — https://www.nature.com/articles/s41467-026-71523-8
- JRC urban green space and wealth — https://joint-research-centre.ec.europa.eu/jrc-news-and-updates/urban-green-spaces-are-scarce-while-climate-and-wealth-impact-access-2026-04-13_en
- Green space inequalities, 26 European cities — https://www.researchgate.net/publication/398290015_Mapping_Green_Space_Inequalities_in_26_European_Cities
- Energy poverty across 214 NUTS2 regions — https://www.sciencedirect.com/science/article/pii/S2772655X24000247
- Unable to keep home warm — https://www.eea.europa.eu/en/analysis/maps-and-charts/proportion-of-people-unable-warm
- Regional living conditions — https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Living_conditions_statistics_at_regional_level
- NHS waiting list breakdowns by deprivation — https://www.england.nhs.uk/2025/07/nhs-publishes-waiting-list-breakdowns-to-tackle-health-inequalities/
- SEND / EHC plan waits — https://www.localgovernmentlawyer.co.uk/education-law/394-education-news/59648-mps-highlight-postcode-lottery-in-wait-times-for-ehc-plans-and-warn-of-send-emergency
- NHS Continuing Healthcare variation — https://www.moore-tibbits.co.uk/news/postcode-lottery-continues-for-nhs-continuing-healthcare-sparking-inequality-concerns/
- Dental care access, 11 countries — https://bmcoralhealth.biomedcentral.com/articles/10.1186/s12903-022-02095-4
- GP shortage in Wallonia — https://www.europeandatajournalism.eu/cp_data_news/belgiums-shortage-of-general-practitioners-a-slow-burning-crisis/
- Banking deserts in Spain — https://www.sciencedirect.com/science/article/pii/S2666954425000146
- ECB access to cash — https://www.ecb.europa.eu/press/economic-bulletin/articles/2022/html/ecb.ebart202205_02~74b1fc0841.en.html
- Air pollution and poverty in European regions — https://www.eurekalert.org/news-releases/1120253
- Rural mobility (Interreg Europe) — https://www.interregeurope.eu/rural-mobility
- Deprivation indices: UK IMD — https://data.geods.ac.uk/dataset/index-of-multiple-deprivation-imd
- SEIFA (Australia) — https://www.abs.gov.au/statistics/detailed-methodology-information/concepts-sources-methods/socio-economic-indexes-areas-seifa-technical-paper/latest-release
- NZ Indices of Multiple Deprivation — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5542612/
- ADI and SVI are not interchangeable — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10553799/
- Australian spatial health inequity — https://onlinelibrary.wiley.com/doi/10.1002/hpja.70156
- NZ Indigenous mental health service access — https://pmc.ncbi.nlm.nih.gov/articles/PMC12465140/

Consumer-tier evidence:
- Household chores and relationship breakdown — https://www.modernhusbands.com/post/house-chores-the-ultimate-guide-to-divide-the-household-labor-for-married-couples
- Shift scheduling bias and turnover — https://rosterlab.com/blog/fairer-scheduling-at-work-reducing-shift-bias
- Nurse scheduling fairness — https://www.shiftable.app/en/blog/checklist
- Sibling caregiving resentment — https://www.homeinstead.co.uk/caregiver-sibling-resentment-over-elderly-parents-is-this-you/
- Carpool burden friction — https://www.hopskipdrive.com/blog/how-the-school-transportation-crisis-is-impacting-parents/
- Free-riding in group projects — https://feedbackfruits.com/blog/eliminating-free-riding-in-group-work
- Open source maintainer burden — https://dev.to/opensauced/the-hidden-cost-of-free-why-open-source-sustainability-matters-1jk7
- Uneven bill splitting — https://expensessplit.com/uneven-bill-split-calculator.html
- Group accommodation cost splitting — https://avantstay.com/blog/split-vacation-rental-fairly/

Format reference:
- PyMC-Marketing example gallery — https://www.pymc-marketing.io/en/stable/gallery/gallery.html
