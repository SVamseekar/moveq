# Agent instructions for moveq

## Commits are not releases

Do not bump `version` in any `pyproject.toml` or `__init__.py`, and do not
create a git tag, unless the user explicitly asks to publish. A finished
work slice is ordinary commits. The version stays at the last released
number until a release is requested.

A slice that only adds tests or docs is a **patch** when it is eventually
released, not a minor — even if you think of it as "the trust release" or
"moveq 0.2".

CI job **Git release rules** (`python scripts/check_release_version.py
--git-rules`) fails the build if package version ≠ latest `v*` tag, unless
`CHANGELOG.md` has a `## [X.Y.Z]` heading for that version (a real release
commit). Do not `--no-verify` to skip the pre-push hook. Do not tag a
feature commit; the publish workflow treats every `v*` tag as a PyPI upload.

## Versioning

Before proposing or applying a version bump, read
[CONTRIBUTING.md](CONTRIBUTING.md) § Versioning. Follow it every time.

This repo versions like **scientific Python** (NumPy, SciPy, scikit-learn), not
like Cargo `0.x`:

- **Patch** (`0.1.1` → `0.1.2`): bug fixes, **including numerical/correctness
  fixes that change metric outputs** so they match the documented definition.
  Docs and packaging too.
- **Minor** (`0.1.2` → `0.2.0`): new public API; on `0.x`, also a breaking API
  change (rename / remove / change signatures); or an *intentional redefinition*
  of a metric.
- Do **not** bump minor because Palma, CI, Gini, or score numbers change after
  a bug fix. scikit-learn `0.24.1` is the analogue.
- `pip install "moveq~=0.1.1"` means `>=0.1.1, ==0.1.*`. A correctness fix
  shipped as `0.2.0` never reaches those users.
- If a patch changes numeric results, say so in `CHANGELOG.md` under that
  patch.

## Release

Follow [docs/publishing.md](docs/publishing.md). One Git tag publishes all four
packages. The tag (without `v`) must match lockstep `version` in every
`pyproject.toml`. Never put a production PyPI token on the laptop or in
secrets.

## Scientific-credibility order

Do not skip ahead unless the user asks. Current order:

1. Independent verification of Gini, Palma, CI, and score (second
   implementation in tests, invariance properties, documented edge cases).
2. Auditable result objects for the equity metrics (new public API → minor
   when released).
3. Research reproductions of published statistics.
4. Interop after GTFS/accessibility tools, not a GTFS parser.

## Metric tests

When adding or changing Gini, Palma, CI, or `compute_score` tests, expected
values must come from an independent second implementation of the documented
formula or a closed-form case, not from calling the production function.
Property tests (permutation, scale invariance, documented bounds) are
required for metric changes. Do not add an external statistics library as
an oracle; their conventions differ.

## Leave alone unless asked

Do not commit or edit `website/` or `examples/benchmark.py` unless the user
explicitly asks.
