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
[security policy](SECURITY.md). Agent sessions should follow
[CLAUDE.md](CLAUDE.md) (working agreement: commits are not releases,
scientific-Python versioning, claims discipline, metric-test oracles).

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

CI runs the same tests on Python 3.10, 3.11, 3.12, and 3.13. The
**Website** job checks the static site (`python scripts/check_website.py`).
**Lint** runs Ruff (error-class rules only). **Dependency audit** runs
`pip-audit` against the installed environment.

```bash
ruff check reference/python scripts tests examples
pip-audit
```

This library has no runtime environment variables. Do not add `.env` files.

## Project layout

```text
moveq/
├── reference/python/     # installable packages (src layout)
├── website/              # static site (Vercel → moveq.souravamseekar.com)
├── docs/                 # user and maintainer documentation
├── examples/             # runnable demos and evidence cases
├── scripts/              # release helpers used by CI
└── .github/workflows/    # Python CI and Trusted Publishing
```

Do not commit virtual environments, `dist/`, caches, secrets, coverage output,
editor state, or agent working files. See `.gitignore`. Python packages are
libraries: install from the version ranges in each `pyproject.toml`. There is
no root lockfile. `website/package-lock.json` is tracked for the static site.

## Branching

`main` is the stable, production-ready branch. Do not develop substantial
work directly on it.

1. Branch from the latest `main`.
2. Use a short-lived name such as `feature/<name>`, `fix/<name>`,
   `refactor/<name>`, or `chore/<name>`.
3. Open a pull request. GitHub requires PRs for `main` (self-review is
   enough; there is no second-human approval requirement).
4. Delete the branch after merge. GitHub already deletes head branches
   on merge.

Do not add GitFlow release/develop branches. A feature branch → PR →
`main` → annotated `vX.Y.Z` tag is the whole release path.

## Pull requests

1. Open a pull request against `main` with a focused change.
2. Use the PR template checklist. Review the complete diff before merge.
3. Add or update tests when behaviour changes.
4. Update `CHANGELOG.md` under **Unreleased** for user-facing changes.
5. Keep the four package versions in lockstep:

   ```bash
   python scripts/check_release_version.py
   ```

6. If you change a public function, class, or CLI flag, update
   [`docs/api_reference.md`](docs/api_reference.md) and any affected guide.

CI must pass before merge. Do not merge with failing required checks.
Packaging is also checked on every PR (`python -m build` plus
`twine check --strict`). The **Website** job must pass for the static
site. Changes under `website/` also get a Vercel preview URL on the pull
request; production is https://moveq.souravamseekar.com.

Unresolved review conversations must be resolved before merge.

## Commit messages

This repository uses [Conventional Commits](https://www.conventionalcommits.org/)
in the form already visible in `git log`. The types in use are:

```
feat:   fix:   docs:   test:   ci:   chore:
```

`refactor:`, `perf:`, and `build:` are also accepted when they describe the
change more accurately. Do not invent types beyond these, and do not restyle
existing history. Never use messages such as "update", "changes", "fix",
"stuff", or "final". One commit is one logical change.

Prose in commits, PRs, issues, docs and the website is predominantly British
(`-ise` / `-isation`); existing API identifiers such as `harmonization` keep
their spelling.

Release commits use `chore: release vX.Y.Z` or `release: vX.Y.Z` as already
in the log.

## Versioning

This project uses [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`,
interpreted the way **scientific Python** libraries do (NumPy, SciPy,
scikit-learn, statsmodels) — not Cargo’s pre-1.0 shift, where the middle number
is the breaking channel.

| Change | Bump | Example |
| --- | --- | --- |
| Breaking public API (rename, remove, or change signatures) | **major** after `1.0`; **minor** while `0.x` | `0.1.2` → `0.2.0` |
| New backwards-compatible public API | **minor** | `0.1.2` → `0.2.0` |
| Bug fix, including numerical / correctness fixes that change outputs | **patch** | `0.1.1` → `0.1.2` |
| Docs, packaging | **patch** | `0.1.1` → `0.1.2` |

### Patch vs minor for metrics

Fixing Gini, Palma, the Concentration Index, or `compute_score` so they match
the **already documented** definition is a **patch**, even if numbers published
under the previous version change. scikit-learn `0.24.1` shipped a numerical
stability fix in `mutual_info_score` as a patch, not `0.25.0`. NumPy bugfix
releases contain no new features or deprecations.

Bump **minor** only when you add a public function, change arguments, or
*intentionally redefine* a metric (a new Palma, not the documented one).

`pip install "moveq~=0.1.1"` means `>=0.1.1, ==0.1.*`. A correctness fix
shipped as `0.2.0` is never installed for those users.

If a patch changes numeric results, say so in `CHANGELOG.md` under that patch
so a study re-run knows to expect different figures.

Do not declare `1.0.0` until the public API is intentionally stable.

Do not bump versions on ordinary PRs. Leave `version` at the last released
number until you are cutting a release; then bump, changelog, and tag in
the same release sequence described below.

CI enforces this: `python scripts/check_release_version.py --git-rules`
(job **Git release rules**). Ordinary commits must keep the lockstep version
equal to the latest `v*` tag. A bump is allowed only when `CHANGELOG.md`
contains `## [X.Y.Z]` for the new version. Optional local hook:

```bash
git config core.hooksPath scripts/git-hooks
```

All four packages share the same version string in their `pyproject.toml` files
(and matching `__version__` in each `__init__.py`). Bump every file in the same
commit. A Git tag `v0.1.0` must match that version exactly or the publish
workflow will fail. The `version` field in [`CITATION.cff`](CITATION.cff) is
kept in the same lockstep so the GitHub citation widget matches the release.

## Releasing

Releases are **not** uploaded from a laptop. CI builds wheels and sdists from a
Git tag and publishes them with PyPI Trusted Publishing (OIDC).

The full maintainer runbook is in [docs/publishing.md](docs/publishing.md).
The short path after Trusted Publishers are configured:

```bash
# 1. Branch from latest main (PRs are required; do not push main directly)
git checkout -b chore/release-X.Y.Z origin/main
# 2. Set version = "X.Y.Z" in all four pyproject.toml files and __init__.py files
# 3. Move CHANGELOG Unreleased notes into [X.Y.Z]
python scripts/check_release_version.py X.Y.Z
git add -u
git commit -m "chore: release vX.Y.Z"
git push -u origin chore/release-X.Y.Z
# Open a PR, wait for CI, merge.

# 4. Tag the merge commit on main, then push the tag (triggers PyPI)
git checkout main && git pull origin main
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

Never store a production PyPI API token in this repository or on your machine.

Never move, delete, or re-point a published `v*` tag. A bad release is
fixed by the next patch (`v1.4.0` stays; ship `v1.4.1`). Rollback is a
new commit and a new version, not a rewritten tag.

## History safety

Never rewrite shared `main` history and never force-push `main`. If a
personal feature branch must be rewritten, use `--force-with-lease`, not
`--force`. Do not run destructive Git commands without checking `git
status`, the current branch, and the remote.
