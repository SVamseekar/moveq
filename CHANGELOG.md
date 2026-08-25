# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

The four distributions — `moveq`, `moveq-core`, `moveq-catalogue`, and
`moveq-cli` — are versioned **in lockstep**. One Git tag publishes all four to
PyPI.

## [Unreleased]

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
