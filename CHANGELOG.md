# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

The four distributions — `moveq`, `moveq-core`, `moveq-catalogue`, and
`moveq-cli` — are versioned **in lockstep**. One Git tag publishes all four to
PyPI.

## [Unreleased]

### Added

- Optional `outcome_kind` on `concentration_index_result` populates
  `EquityResult.interpretation` (location of a benefit or burden; never
  fairness or causation). Omission preserves descriptive-only output.
- `weight_kind` on `gini_result`, `palma_result`, and
  `concentration_index_result`. Omission records `"population"` and
  warns; arithmetic is unchanged.
- `missing_policy` on `compute_score`: `reweight` (default), `as_zero`,
  `exclude`, `bounds`. `ScoreResult` gains `parameters` and `bounds`.
  `exclude` and incomplete `bounds` return `score=None` (no midpoint).
- Concentration Index `variant` (`standard`, `generalized`, `erreygers`,
  `wagstaff_normalized`) recorded in `parameters`. `method` stays
  `wagstaff-covariance`. Bounded outcomes warn; the library does not
  switch variant.
- CI coverage measurement for `moveq_core` and `moveq_catalogue` with a
  98% floor (observed ~99% on 322 statements).

### Changed

- Website no longer offers `conda install -c conda-forge moveq` (the package
  is not on conda-forge) and no longer claims a browser WebAssembly runtime.
  `moveq-core` is described as a pure-NumPy engine with no I/O or GIS
  dependencies.
- Documentation no longer describes population weighting or missing-term
  reweighting as inherently correct.

### Added

- `CITATION.cff` at the repository root so GitHub can render a citation
  widget. Version is kept in lockstep with the packages; no DOI (Zenodo
  is a separate, deferred decision).
- Commit-message types already in use (`feat`, `fix`, `docs`, `test`,
  `ci`, `chore`) recorded in `CONTRIBUTING.md`, with a pointer to
  `CLAUDE.md`.

- CI job **Git release rules** fails if package version drifts from the
  latest `v*` tag unless `CHANGELOG.md` has a `## [X.Y.Z]` release heading.
- Independent second-implementation tests for Gini, Palma, the Concentration
  Index, and composite scores, plus scale/permutation invariance, documented
  bounds, and empty / single-observation cases.
- `EquityResult` and `gini_result` / `palma_result` /
  `concentration_index_result` for auditable Gini, Palma, and Concentration
  Index outputs. The existing `compute_*` functions still return `float`.
  `moveq gini|palma|ci --json` emits `EquityResult.to_dict()`.

## [0.2.0] — 2026-09-06

Required `rank_direction` on the Concentration Index, and an undefined
result when mean service is zero. This is a minor bump: a required
keyword argument is a signature change, and treating a cancelled mean
as undefined is an intentional redefinition (previously `0.0`).

### Changed

- Guides no longer treat a 5% Concentration Index change as triggering a
  Title VI review. moveq reports distributional change; it does not
  determine compliance.
- `compute_concentration_index` and `concentration_index_result` now
  require `rank_direction` (`higher_is_advantaged` or
  `higher_is_disadvantaged`). There is no default: omitting it is a
  `TypeError`. Positive CI is advantage-concentrated; negative CI is
  disadvantage-concentrated.
- A zero or cancelled mean service makes the relative Concentration
  Index **undefined**. The result API returns `value=None` with
  `status="undefined"`; the scalar API raises `UndefinedMetricError`.
  Previously this returned `0.0`. `zero_mean="legacy_zero"` restores the
  old number and emits `DeprecationWarning`.
- `moveq ci` requires `--rank-direction` (hyphen form). An undefined
  result exits with code `3`.

Migration:

```python
# Before (0.1.x) — direction ambiguous, sign could be wrong
ci = compute_concentration_index(service, imd_rank, population)

# After — IMD rank: 1 = most deprived, so higher = more advantaged
ci = compute_concentration_index(
    service, imd_rank, population,
    rank_direction="higher_is_advantaged",
)
```

Callers must check their rank column. A caller who declared the wrong
direction was already getting a wrong sign; this change surfaces that
rather than introducing it.

- Website guides no longer claim GTFS parsing, H3 aggregation, routing,
  or Kepler/GPU rendering as moveq capabilities. Remaining examples use
  the required `rank_direction` argument. A 5% CI change is not treated
  as a Title VI trigger.

## [0.1.2] — 2026-08-25

Correctness patch. Signatures are unchanged. Palma, the Concentration Index,
Gini, and `compute_score` now match the documented definitions, so some
figures computed with `0.1.1` will change (coarse geographies, tied ranks,
all-zero service, invalid input).

### Changed

- Palma ratio splits areal units that straddle the 40% and 90% population
  cuts, instead of including or dropping whole units.
- Concentration Index assigns tied ranks a shared group-midpoint fractional
  rank, so input order among ties no longer changes the result.
- Palma of an all-zero service distribution is `1.0` (equality), not `inf`.
- `compute_score` keeps `n_areas=None` when every term is missing (it
  previously coerced that to `0`).

### Fixed

- Gini with zero total service returns `0.0` instead of dividing by zero.
- Concentration Index is defined when mean service is negative (it previously
  returned `0`).
- Concentration Index ignores unpopulated units instead of producing `NaN`.
- Gini, Palma, and the Concentration Index reject 2-D input with a clear
  error instead of a NumPy broadcast failure or a silent 2-D result.
- Composite scores reject non-finite term values rather than clipping `inf`
  to `1` or propagating `NaN`.
- Design weights must be finite and strictly positive.

## [0.1.1] — 2026-08-25

Documentation-only release. No algorithm changes.

### Changed

- Rewrote all four package READMEs so PyPI project pages explain *what*
  each metric and catalogue action means, not only how to call the API.

## [0.1.0] — 2026-08-25

Initial library stack (source on GitHub; first PyPI upload follows the `v0.1.0`
tag).

### Added

- `moveq-core`: population-weighted Gini, Palma ratio, Wagstaff Concentration
  Index, weighted composite scoring with missing-term renormalization, and
  optional pandas helpers for vulnerability indexing.
- `moveq-catalogue`: `same` / `replace` / `omit` registry so cross-country
  section catalogues cannot silently drop a base section.
- `moveq`: umbrella package re-exporting the core and catalogue APIs.
- `moveq-cli`: CSV/JSON command-line interface (`gini`, `palma`, `ci`, `score`,
  `catalogue validate`).
