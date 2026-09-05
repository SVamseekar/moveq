# moveq Example Gallery — Design

**Date:** 2026-09-05
**Status:** Design, pending implementation plan
**Supersedes:** the 52-entry draft committed in ae0afe7

---

## 1. Thesis

People routinely report distributions as scalars — averages, counts, thresholds and
ratios — and those scalars can hide who is actually affected. moveq makes the
distributional dimension measurable and auditable.

The gallery exists to make that case. It is not a demonstration that Python can
calculate inequality statistics; it is an argument that a particular class of
decisions is being made on evidence that has thrown away the relevant information.

Each example must be a different real-world manifestation of that problem. Eight
genuinely different analytical jobs are worth more than eighteen variations on four.

## 2. Inclusion test

Every candidate must answer all seven questions convincingly. Any that cannot is
rejected, and the reason is recorded in the appendix.

1. **Who actually has this problem?** A named actor: a planner, ministry, researcher,
   regulator. Not "people" or "a group of friends".
2. **What do they currently measure to make the decision?** A specific scalar in
   current practice.
3. **What does that measurement throw away?** Specifically. "It doesn't show
   inequality" is not an answer.
4. **What decision changes when the distribution is revealed?** If no real decision
   or interpretation changes, reject.
5. **What is the primary analytical job**, with the domain nouns stripped out?
6. **Is that job different from every other example's job?** If two entries reduce to
   the same job, merge them and pick the strongest domain.
7. **Can the current moveq API express it?** If not, it is a future capability, not a
   gallery entry.

Two rules govern the set as a whole:

- **Coverage is not a reason.** No example exists because a function needs exercise.
  Functions appear where the problem calls for them; if `moveq-cli` or
  `moveq-catalogue` ends up in one example each, that is the correct number.
- **The API is fixed.** No new library function is added to make an example possible.

## 3. The eight examples

Ranked by how strongly each makes the case for the library.

---

### 1. The average improved. Did inequality?

**Analytical job:** Isolating the divergence between a mean and a distribution across
two periods — the phenomenon itself, taught directly.

**Actor:** A policy evaluator signing off an intervention, or an analyst writing the
post-implementation review.

**Problem:** An intervention has completed. The evaluation must state whether it
worked.

**Current practice:** Compare the mean before and after. If it improved, the
intervention succeeded.

**Information lost:** A rise in the mean is fully compatible with the worst-served
falling further behind. Aggregate improvement and distributional deterioration are
indistinguishable in a scalar.

**moveq contributes:** `gini_result` and `concentration_index_result` computed on both
periods, showing the mean rising while concentration worsens.

**Decision affected:** Whether the programme is judged successful and extended.

**Data:** Constructed. This is the one example where synthetic data is the right
choice: the purpose is to isolate a mathematical phenomenon, and real data would
introduce confounds that obscure it.

**Buildability:** Synthetic — by design, clearly labelled.

**Why different:** Every other two-period example is empirical and asks what happened
in a specific case. This one is constructed to make the phenomenon unmistakable, and
is the conceptual flagship the others depend on.

---

### 2. Did the new capacity reach the people who needed it?

**Analytical job:** Two-period empirical evaluation — did a change in provision track
need, or run against it?

**Actor:** A transport authority or utility regulator evaluating an infrastructure
programme, deciding where the next tranche goes.

**Problem:** A city installed 1,000 EV charging points. The programme reports
completion. The question for the next budget is whether it reached the people it was
meant to reach.

**Current practice:** Count of units installed, or percentage increase in provision.

**Information lost:** Whether new capacity landed where provision was already good.
An installation count is silent on the population underneath each unit and on the
socioeconomic position of the areas that gained.

**moveq contributes:** Population-weighted `gini_result` before and after, plus
`concentration_index_result` against a deprivation rank, showing whether the gain
accrued to already-advantaged areas.

**Decision affected:** Whether the next investment is redirected.

**Data:** National EV charging point registries with small-area geography; deprivation
rank from IMD or an equivalent national index.

**Buildability:** Buildable.

**Why different:** Example 1 is constructed to teach; this is an empirical evaluation
of a real programme with a real next decision attached.

**Absorbs:** "Five pharmacies closed — whose access disappeared?" and "Who gained from
the new rail station?" Both reduce to the same job — capacity changed, did the change
track need — differing only in sign and noun. Pharmacy closure data by area could not
be sourced (see appendix); the rail case is the same analysis on a different asset.
One example, done well, is worth more than three.

---

### 3. Where should the one remaining unit go?

**Analytical job:** Allocation under a hard constraint — ranking candidate areas by
current burden when there is exactly one resource to place.

**Actor:** A health authority with one additional weekend clinic session to allocate;
equivalently a transport planner with one route to add.

**Problem:** Several candidate areas want the resource. Population and headline demand
look similar.

**Current practice:** Total ridership, appointment volume, or projected utilisation —
a cost-benefit case that favours areas already generating demand.

**Information lost:** Utilisation measures revealed demand, which is suppressed
precisely where provision is worst. Two areas of 20,000 people with 100 and 60
service units look comparable on population and may look comparable on utilisation,
while carrying entirely different access burdens.

**moveq contributes:** Population-weighted service levels across candidates, plus
`concentration_index_result` against deprivation to establish whether existing
capacity already favours better-off populations.

**Decision affected:** Which area receives the resource.

**Data:** Service provision by small area (GP appointment sessions, bus service
kilometres), population, national deprivation rank.

**Buildability:** Buildable.

**Why different:** Examples 1 and 2 evaluate what happened. This one is prospective
and comparative: no intervention has occurred, and the output is a ranking that
selects among candidates.

**Absorbs:** "Where should the next bus go?" — identical mechanics, different asset.

---

### 4. Who are the ones outside the threshold?

**Analytical job:** Turning a pass/fail threshold back into a distribution — locating
and characterising the excluded minority.

**Actor:** A local authority education planner deciding where school access investment
is needed.

**Problem:** The authority reports that 97% of children are within acceptable distance
of a school place. The 3% are a rounding error in the headline and a live problem in
the casework.

**Current practice:** Percentage meeting a threshold.

**Information lost:** Three things at once — who the excluded are, how far beyond the
threshold they sit, and whether exclusion is socioeconomically concentrated. A
threshold discards magnitude entirely: an area 200 metres beyond the line and one
5 kilometres beyond are both simply "outside".

**moveq contributes:** `concentration_index_result` on access against deprivation
rank, and `gini_result` on the underlying distances rather than the binary outcome.

**Decision affected:** Where access investment is targeted.

**Data:** School place allocation and home-to-school distance statistics; IMD rank.

**Buildability:** Buildable.

**Why different from example 5:** A threshold discards *magnitude below a line*; a
mean discards *the shape of a tail*. Different information lost, different reconstruction.

**Absorbs:** "GP deserts in Wallonia" — "half of communes are shortage areas" is the
same threshold-count job on a different service.

---

### 5. Does the average describe everyone?

**Analytical job:** Single-period reconstruction of a distribution from a reported mean.

**Actor:** A hospital trust or ambulance service reporting performance to a regulator.

**Problem:** Waiting time performance must be reported, and the reported figure is
treated as descriptive of the service patients receive.

**Current practice:** The arithmetic mean — "average waiting time is 24 minutes" —
sometimes accompanied by a median or a 95th percentile, but reported and read as a
single headline figure.

**Information lost:** The tail and its composition. A 24-minute mean is compatible with
near-uniform waits and with most patients waiting 15 minutes while a minority wait
two hours — and with those minorities being systematically the same people.

**moveq contributes:** `gini_result` on waiting times weighted by population served,
plus `concentration_index_result` against deprivation to test whether long waits fall
disproportionately on particular communities.

**Decision affected:** Whether reported performance improvement is accepted as
equitable, or triggers targeted investigation.

**Data:** NHS publishes waiting list breakdowns by deprivation, so the data already
exists in the required shape.

**Buildability:** Buildable.

**Why different from example 4:** See above — mean versus threshold discard different
things.

---

### 6. Does provision match vulnerability when the data is patchy?

**Analytical job:** Composite scoring across heterogeneous inputs with missing terms
handled explicitly.

**Actor:** A member-state ministry drafting a Social Climate Plan.

**Problem:** All 27 EU member states are legally required to submit plans identifying
vulnerable households for energy and transport poverty measures, against a fund of
€86.7bn across 2026–2032. Vulnerability is multi-dimensional by legal definition —
affordability and access, in national and spatial context.

**Current practice:** National prevalence rates ("9.2% cannot keep their home warm"),
or bespoke composites built per state.

**Information lost:** Two distinct things. First, whether the burden is concentrated
among poorer households or merely higher in colder countries. Second — and this is the
part no scalar can carry — which component terms were missing for which regions.
States have unequal data coverage, and a composite that silently treats a missing term
as zero produces a different ranking from one that reweights the remaining terms.

**moveq contributes:** `compute_score` with explicit missing-term reweighting, so
regions with partial data are scored on what exists rather than penalised for absence,
with `ScoreResult.dropped` and `weight_used` recording exactly what happened;
`concentration_index_result` for the burden question.

**Decision affected:** Which regions and households are designated vulnerable, and
therefore where the money goes.

**Data:** Eurostat energy poverty indicators by NUTS2; EU-SILC income data.

**Buildability:** Buildable.

**Why different:** The only example whose central difficulty is incomplete and
inconsistent input data rather than a discarded distribution.

---

### 7. Can these countries' figures be compared at all?

**Analytical job:** Schema reconciliation across jurisdictions — making a comparison
possible, and recording what does not map.

**Actor:** A comparative researcher working across the UK, US, EU, Australia and New
Zealand.

**Problem:** Every jurisdiction has a small-area deprivation index and none of them
agree. The UK IMD ranks ~33,000 LSOAs across seven domains. Australia's SEIFA
publishes four separate indexes. New Zealand runs NZDep and the NZ IMD in parallel.
In the US, ADI and SVI are documented as not interchangeable. EU-SILC is
income-based at a coarser geography.

**Current practice:** A private spreadsheet mapping, or quiet omission of the
sections that do not align, with the omission invisible in the published result.

**Information lost:** Which domains were treated as equivalent, which were substituted,
and which were dropped. A reader cannot tell whether "deprivation" means the same
thing on both sides of a comparison.

**moveq contributes:** `moveq-catalogue`'s `same`/`replace`/`omit` contract, with
`validate()` and `unregistered()` turning silent omission into an explicit, checkable
declaration.

**Decision affected:** Whether the cross-country comparison is defensible enough to
publish.

**Data:** Published index documentation from each jurisdiction.

**Buildability:** Buildable.

**Why different:** The only example where the problem is upstream of measurement.
Nothing is being computed yet; the question is whether the inputs can legitimately be
placed side by side. It is also the one job with no straightforward R or Stata
equivalent.

---

### 8. Will this number survive being challenged?

**Analytical job:** Result-level provenance — reconstructing what a published figure
actually did.

**Actor:** A researcher responding to peer review, or an analyst answering a regulator
or auditor.

**Problem:** A figure has been published. A reviewer asks how many areas were
excluded, what happened to zero-population units, and what the parameters were.

**Current practice:** A number, and a methods paragraph written from memory some
months after the analysis.

**Information lost:** Everything about the computation except its output. Standard
tools return a float; the exclusions, warnings and parameter choices live only in the
analyst's script, if anywhere.

**moveq contributes:** `EquityResult` carries `n_dropped`, `n_areas`,
`total_population`, `warnings`, `note`, `parameters` and `context` alongside the value,
and `to_dict()` serialises the lot. The example shows a Gini computed on data with
zero-population areas and demonstrates what the result records about its own
construction.

**Decision affected:** Whether the finding stands when challenged.

**Data:** Any dataset with realistic imperfections; the example uses one of the
buildable datasets above.

**Buildability:** Buildable.

**Why different from example 9's validation role:** This is provenance of *your* result
— what this computation did to this data. Validation against published figures is a
different question, addressed below.

---

## 4. Candidate held for review

**Independent validation against published figures.** Reproducing a peer-reviewed
result — the within-city accessibility inequality figures in the 15-minute city
literature — would demonstrate that moveq's implementation agrees with independently
published numbers. That is a real and distinct job from example 8: implementation
correctness rather than result provenance.

It is held rather than committed because it depends on obtaining the study's
underlying data at sufficient resolution, which has not been confirmed. If the data
is available, it becomes example 9. If not, it is not replaced by a substitute.

## 5. Rejected examples

Recorded so the reasoning survives, and so tempting candidates are not silently
regenerated later.

**All "equal policy, unequal burden" entries** — same parking allowance, same
childcare benefit, same travel reimbursement, same commute allowance, same hybrid
policy, same remote-work policy. Sixteen entries in the previous draft. They reduce
to one job: equal input, unequal burden, compute Gini. Different nouns are not
different applications.

**Household and small-group scenarios** — chore splits, hotel room allocation, wedding
costs, group trips, fair meeting points, rent-versus-commute balancing. Three failures:
the actor is not a named decision-maker, no institutional decision changes, and the
statistics are not well-posed at n≈5. Palma is undefined at that scale and there is no
deprivation rank. These were the origin of the project and are recorded here as
deliberately excluded, not overlooked.

**Domain variations absorbed into surviving examples** — pharmacy closures and rail
station gains into example 2; next-bus allocation into example 3; GP deserts into
example 4. Each was the same analytical job on a different asset.

**Data-blocked candidates** — pharmacy access by area (the sector evidence is
qualitative; no per-area provision counts found), library closures by community, food
bank capacity by area, energy billing complaints by region (only national totals
published). Real problems, no locatable data. Listed as contribution-wanted rather
than built with substitutes.

**Weak candidates** — childcare cost comparison (country-level only, n≈27, no
within-country distribution); regional NHS backlog growth (the +113% versus +71%
comparison is already legible; a Gini over seven regions adds nothing).

**Withdrawn API change** — `spread_result()`. The previous draft proposed it as a
small-n counterpart to Palma. Its only justification was making household examples
possible, and with those examples rejected the justification disappears. It does not
survive on independent grounds either: at n≈5 `compute_gini` is already well-defined
and "who has it worst" is `max(values)`, which needs neither a library function nor an
`EquityResult` wrapper. A Palma counterpart requires population mass to split at
40/90, which does not exist at that scale. The library drives the gallery, not the
reverse.

## 6. Coverage, observed

Coverage is recorded as an outcome, not a target.

| Component | Appears in |
|---|---|
| `gini_result` / `compute_gini` | 1, 2, 4, 5, 8 |
| `concentration_index_result` | 1, 2, 3, 4, 5, 6 |
| `compute_score` | 6 |
| `EquityResult` audit fields | 8, and displayed throughout |
| `moveq-catalogue` | 7 |
| `moveq` (re-export) | all — the default import |
| `palma_result` | none |
| `moveq-cli` | none as a subject |
| `moveq[frames]` | incidental, where data arrives as CSV |

Two absences are deliberate and worth stating plainly.

**Palma appears in no example.** It needs enough units for the 40/90 split to be
stable, and each surviving example either works at small unit counts or is better
served by the Concentration Index, which uses a socioeconomic rank rather than
position in the outcome distribution. Manufacturing a Palma example would violate the
inclusion test.

**`moveq-cli` is not the subject of any example.** It is a delivery mechanism, not an
analytical job. Where an example's data arrives as CSV, the example may show the
command-line equivalent alongside the Python — but no example exists to demonstrate
the CLI.

## 7. Card schema

Every card carries the same fields, in this order:

| Field | Content |
|---|---|
| **The real question** | The decision, in the words of the actor making it |
| **Normally reported as** | The scalar in current practice |
| **What it throws away** | Specifically what information is lost |
| **What moveq shows** | The metric and the finding |
| **What changes** | The decision that moves |

Plus the actor, the data source with retrieval date and licence, and a buildability
status.

## 8. Implementation architecture

**Structure.** Each example is a runnable `.py` under `examples/<slug>/`, following
the existing `examples/basic_equity/run.py` pattern. Each produces one chart, which
becomes its gallery thumbnail.

**Execution.** Examples run in CI; a broken example fails the build. This follows the
existing `scripts/check_website.py` discipline and prevents the documentation rot that
hand-maintained code samples suffer.

**Data.** Small committed CSV extracts with provenance notes, not live downloads.
Live fetching would make CI depend on external availability and licensing. Each
dataset records its source URL, retrieval date and licence. moveq takes arrays and
CSVs; the gallery must not turn it into an ingestion or GIS platform.

**Site.** Gallery index at `website/examples/`, between `guides/` and `reference/` —
the missing middle documentation layer. Static HTML consistent with the existing site.
Cards show thumbnail, title, the real question as a one-line description, and a
buildability badge. No filtering or search in the first version; eight to nine entries
do not need it.

**No library changes.** The current moveq API is the constraint.

## 9. Delivery

Examples ship individually; a card is published only when its example runs.

**First three — the argument in full:**

- Example 1, the average improved (the phenomenon, taught directly)
- Example 5, does the average describe everyone (the phenomenon, empirical, on data
  already published in the right shape)
- Example 8, will this number survive challenge (the differentiator)

These three state the thesis and demonstrate why moveq rather than a Gini function
copied from a blog post.

**Then:** examples 2, 3, 4 — the evaluation, allocation and threshold jobs, all
requiring data acquisition.

**Then:** examples 6 and 7 — the statutory composite and the harmonization case, the
two heaviest builds and the two strongest institutional arguments.

## 10. Risks

**Data acquisition dominates.** Locating, cleaning and licence-checking real data is
most of the work; the moveq calls are a few lines each. Mitigated by committing small
extracts rather than building pipelines.

**Eight examples may read as thin next to galleries with fifty.** The mitigation is the
gallery's own framing: each card names a distinct analytical job, and the set is
presented as eight different problems rather than eight demonstrations. A ninth
example that repeats a job would weaken the argument rather than strengthen it.

**The public "dumb pipes" claim needs correcting.** Existing consumer meeting-point
products already minimise the longest journey rather than using naive averages. Any
site copy asserting otherwise is factually wrong and should be revised independently
of this work.

## 11. Sources

Statutory and policy:
- Social Climate Fund — https://eur-lex.europa.eu/EN/legal-content/summary/social-climate-fund.html
- EU transport poverty definition — https://cer.be/images/publications/facts-figures/250602_CER_Factsheet_Transport_poverty.pdf
- Energy Poverty Advisory Hub indicators — https://energy-poverty.ec.europa.eu/epah-indicators

Data and research:
- NHS waiting list breakdowns by deprivation — https://www.england.nhs.uk/2025/07/nhs-publishes-waiting-list-breakdowns-to-tackle-health-inequalities/
- Energy poverty across 214 NUTS2 regions — https://www.sciencedirect.com/science/article/pii/S2772655X24000247
- Unable to keep home adequately warm — https://www.eea.europa.eu/en/analysis/maps-and-charts/proportion-of-people-unable-warm
- Regional living conditions statistics — https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Living_conditions_statistics_at_regional_level
- 15-minute city accessibility inequality — https://www.nature.com/articles/s42949-023-00133-w

Deprivation indices:
- UK Index of Multiple Deprivation — https://data.geods.ac.uk/dataset/index-of-multiple-deprivation-imd
- SEIFA, Australia — https://www.abs.gov.au/statistics/detailed-methodology-information/concepts-sources-methods/socio-economic-indexes-areas-seifa-technical-paper/latest-release
- NZ Indices of Multiple Deprivation — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5542612/
- ADI and SVI are not interchangeable — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10553799/

Format reference:
- PyMC-Marketing example gallery — https://www.pymc-marketing.io/en/stable/gallery/gallery.html
