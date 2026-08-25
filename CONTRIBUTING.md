# Contributing to moveq

Thank you for contributing. This repository is a **monorepo** of four Python
packages that are versioned and released together:

| PyPI name | Import / CLI | Path |
| --- | --- | --- |
| `moveq-core` | `import moveq_core` | `reference/python/moveq-core` |
| `moveq-catalogue` | `import moveq_catalogue` | `reference/python/moveq-catalogue` |
| `moveq` | `import moveq` | `reference/python/moveq` |
| `moveq-cli` | `moveq` command | `reference/python/moveq-cli` |

Please also read the [Code of Conduct](CODE_OF_CONDUCT.md) and the
[security policy](SECURITY.md).

## Development setup

Requires Python 3.10 or newer.

```bash
git clone https://github.com/SVamseekar/moveq.git
cd moveq
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

python -m pip install --upgrade pip
pip install -e "reference/python/moveq-core[frames,test]"
pip install -e "reference/python/moveq-catalogue[test]"
pip install -e "reference/python/moveq[test]"
pip install -e "reference/python/moveq-cli[test]"
```

Run the test suite from the repository root:

```bash
pytest -v
python examples/basic_equity/run.py
```

CI runs the same tests on Python 3.10, 3.11, 3.12, and 3.13.

## Project layout

```text
moveq/
├── reference/python/     # installable packages (src layout)
├── docs/                 # user and maintainer documentation
├── examples/             # runnable demos
├── scripts/              # release helpers used by CI
└── .github/workflows/    # CI and Trusted Publishing
```

Do not commit virtual environments, `dist/`, caches, or secrets. See `.gitignore`.

## Pull requests

1. Open a pull request against `main` with a focused change.
2. Use the PR template checklist.
3. Add or update tests when behaviour changes.
4. Update `CHANGELOG.md` under **Unreleased** for user-facing changes.
5. Keep the four package versions in lockstep:

   ```bash
   python scripts/check_release_version.py
   ```

6. If you change a public function, class, or CLI flag, update
   [`docs/api_reference.md`](docs/api_reference.md) and any affected guide.

CI must pass before merge. Packaging is also checked on every PR (`python -m build`
plus `twine check --strict`).

## Versioning

This project uses [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

| Change | Bump |
| --- | --- |
| Breaking public API | **major** (`1.2.3` → `2.0.0`) |
| New backwards-compatible API | **minor** (`1.2.3` → `1.3.0`) |
| Bug fix, docs, packaging | **patch** (`1.2.3` → `1.2.4`) |

While the stack is still `0.x`, a **minor** bump may also include breaking API
changes (`0.1.0` → `0.2.0`). Patch remains bug-fix only. Do not declare `1.0.0`
until the public API is intentionally stable.

All four packages share the same version string in their `pyproject.toml` files.
Bump every file in the same commit. A Git tag `v0.1.0` must match that version
exactly or the publish workflow will fail.

## Releasing

Releases are **not** uploaded from a laptop. CI builds wheels and sdists from a
Git tag and publishes them with PyPI Trusted Publishing (OIDC).

The full maintainer runbook is in [docs/publishing.md](docs/publishing.md).
The short path after Trusted Publishers are configured:

```bash
# 1. Set version = "X.Y.Z" in all four pyproject.toml files
# 2. Move CHANGELOG Unreleased notes into [X.Y.Z]
git add -u
git commit -m "chore: release vX.Y.Z"
git push origin main

git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

Never store a production PyPI API token in this repository or on your machine.
