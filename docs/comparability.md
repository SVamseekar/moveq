# Comparability of a distributional difference

A difference of two inequality results is meaningful only when baseline and proposal share geography, vintage, denominators, units, and missing-data treatment. Almost none of the real gallery datasets satisfy that between years. Boundaries change, populations are re-estimated, and methods are revised. A tool that compared those vintages would report a change that can be entirely an artefact of the denominator.

This note answers the eight design questions. It does not ship a diff product, a GitHub Action, or equity regression tests.

## Decision

A general comparison tool is **not feasible** inside moveq. The library cannot see whether two tables are the same places. Shipping a silent comparator would create the confident-but-wrong result this project exists to avoid.

What remains is a controlled demonstration path, built only where comparability is known because the pair was constructed that way. That demonstration is not a capability of the library. It is labelled as a demonstration. It uses difference intervals when those exist, so a reported change can be told from noise. It does not define "residents worse off" when boundaries move.

The name is `distributional difference`. It is not called CI. Concentration index and confidence interval already use those letters.

## The eight questions

1. **How is comparability verified?** It is asserted by the person who built the pair, not detected from the arrays. moveq has no geometry, no vintage, and no denominator metadata unless the caller passes it. Automatic verification would pretend to know something the arrays do not contain.

2. **What happens when inputs are not comparable?** The general tool is not built, so it cannot warn-and-continue. A demonstration refuses to run unless the caller passes an explicit attestation that geography, vintage, denominators, units, and missing-data treatment match. There is no default that proceeds.

3. **Are thresholds only meaningful beside a difference interval?** Yes. A cutoff on "Gini rose by 0.02" without an interval treats noise as a finding. Any demonstration that reports a change reports the interval on the difference, not the gap between two separate intervals.

4. **Is the unit of comparison the areal unit or the population?** The resampled row is the areal unit, and the index inside each draw is population-weighted. That is a statement about the estimator. It is not a count of people made worse off.

5. **How is "residents worse off" defined when boundaries change?** It is not defined. People do not keep an identity across a boundary revision inside this library. The demonstration does not print that count unless the units are the same constructed rows and the outcome is on those rows. Changing boundaries are a refusal, not a footnote.

6. **Does this belong in `moveq-cli` or a separate package?** Neither, as a product. The CLI does not gain a `diff` command. A new package would advertise the tool this note rejects.

7. **Does another package conflict with a small core?** Yes, if the package exists to compare arbitrary tables. Core stays the inequality functions it already has. A demonstration script may call those functions. It does not add a second implementation.

8. **What is the name?** `distributional difference`. Not "Equity CI", not "equity regression", not a check that fails a pull request.
