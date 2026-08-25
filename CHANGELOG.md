# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

The four distributions — `moveq`, `moveq-core`, `moveq-catalogue`, and
`moveq-cli` — are versioned **in lockstep**. One Git tag publishes all four to
PyPI.

## [Unreleased]

### Added

- CI job **Git release rules** fails if package version drifts from the
  latest `v*` tag unless `CHANGELOG.md` has a `## [X.Y.Z]` release heading.
- Independent second-implementation tests for Gini, Palma, the Concentration
  Index, and composite scores, plus scale/permutation invariance, documented
  bounds, and empty / single-observation cases.
- `EquityResult` and `gini_result` / `palma_result` /
  `concentration_index_result` for auditable Gini, Palma, and Concentration
  Index outputs. The existing `compute_*` functions still return `float`.
  `moveq gini|palma|ci --json` emits `EquityResult.to_dict()`.

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
