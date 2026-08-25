# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

The four distributions — `moveq`, `moveq-core`, `moveq-catalogue`, and
`moveq-cli` — are versioned **in lockstep**. One Git tag publishes all four to
PyPI.

## [Unreleased]

### Added

- GitHub Actions publish workflow using PyPI Trusted Publishing (OIDC). Production
  uploads are triggered by `v*` tags; TestPyPI uploads are triggered by
  workflow dispatch. No production PyPI token is stored in the repository.
  Each package uses its own GitHub environment (`pypi-moveq`,
  `pypi-moveq-core`, …) because PyPI pending publishers are unique per
  workflow + environment.
- CI now also builds wheels/sdists and runs `twine check --strict`.
- Package metadata for PyPI: authors, classifiers, keywords, and project URLs.
- Maintainer and contributor docs: publishing runbook, contributing guide,
  security policy, code of conduct, issue/PR templates, and Dependabot for
  GitHub Actions.

## [0.1.0] — 2026-08-17

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
