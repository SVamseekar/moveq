# Agent instructions for moveq

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

## Leave alone unless asked

Do not commit or edit `website/` or `examples/benchmark.py` unless the user
explicitly asks.
