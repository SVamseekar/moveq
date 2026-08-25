# Publishing moveq to PyPI

This is the maintainer runbook. Contributors should read
[CONTRIBUTING.md](../CONTRIBUTING.md) instead.

**Rule:** GitHub holds source. PyPI holds built wheels (`.whl`) and source
archives (`.tar.gz`). CI builds those files from a version tag and uploads them
with [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC).
Do **not** store a production PyPI API token on your machine or in GitHub
secrets.

```text
main (reviewed, tests green)
   ↓
lockstep version bump + CHANGELOG
   ↓
git tag vX.Y.Z && git push origin vX.Y.Z
   ↓
GitHub Actions workflow: publish.yml
   ↓
test on 3.10–3.13 → build four packages → twine check
   ↓
OIDC upload to PyPI → GitHub Release with the same artifacts
```

## Packages published together

One tag publishes four PyPI projects. Versions must be identical.

| PyPI project | What users install | Built from |
| --- | --- | --- |
| [moveq](https://pypi.org/project/moveq/) | `pip install moveq` | `reference/python/moveq` |
| [moveq-core](https://pypi.org/project/moveq-core/) | `pip install moveq-core` | `reference/python/moveq-core` |
| [moveq-catalogue](https://pypi.org/project/moveq-catalogue/) | `pip install moveq-catalogue` | `reference/python/moveq-catalogue` |
| [moveq-cli](https://pypi.org/project/moveq-cli/) | `pip install moveq-cli` | `reference/python/moveq-cli` |

`moveq` depends on `moveq-core` and `moveq-catalogue`. `moveq-cli` depends on
`moveq`. Users of the Python API normally only need `pip install moveq`.

Each package's `README.md` is the long description shown on PyPI. Keep those
files self-contained and use **absolute** GitHub URLs for documentation links
so they render on both GitHub and PyPI.

## Versioning

Canonical policy: [CONTRIBUTING.md](../CONTRIBUTING.md) (scientific Python, not
Cargo `0.x`). Decision at bump time:

| Kind of change | Version bump | Example |
| --- | --- | --- |
| Breaking public API | major after `1.0`; **minor** while `0.x` | `0.1.2` → `0.2.0` |
| Compatible new API | minor | `0.1.2` → `0.2.0` |
| Bug fix, including metric-output corrections | **patch** | `0.1.1` → `0.1.2` |
| Docs, packaging | patch | `0.1.1` → `0.1.2` |

Do **not** bump minor because Palma / CI / Gini / score numbers change after a
correctness fix. `~=0.1.1` only receives `0.1.*`; shipping the fix as `0.2.0`
hides it from pinned users. Stay on `0.x` until you freeze the public API as
`1.0.0`.

Set `version = "X.Y.Z"` in **all four** `pyproject.toml` files in the same
commit. The publish workflow runs `scripts/check_release_version.py` and
refuses to upload if the Git tag (without the leading `v`) does not match.

## One-time setup (Trusted Publishing)

Do this before the first TestPyPI or PyPI upload. You need a
[PyPI](https://pypi.org/account/register/) account **and** a separate
[TestPyPI](https://test.pypi.org/account/register/) account.

### 1. Why each package has its own GitHub environment

PyPI pending publishers are unique on
`(GitHub owner, repository, workflow filename, environment)`. You cannot
register the same tuple for two project names. That is why this error appears
if every package uses environment `pypi`:

> A pending trusted publisher matching this configuration has already been
> registered for a different project name.

Once a project **exists**, the same workflow can be added as an ordinary
publisher on multiple projects. The uniqueness rule applies to **pending**
publishers (first-time name creation). This monorepo therefore uses **one
GitHub environment per package** so all four names can be created with OIDC
and no API token.

PyPI also allows **at most three pending publishers per account**. Register
three first (`moveq`, `moveq-core`, `moveq-catalogue`). After those uploads
succeed, each pending publisher becomes an ordinary publisher and the slot
frees — then add `moveq-cli`. Do not try to register all four at once.

### 2. GitHub environments

Create these eight [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
under **Settings → Environments**. Names must match exactly:

| Environment | PyPI project | Index |
| --- | --- | --- |
| `pypi-moveq` | `moveq` | production |
| `pypi-moveq-core` | `moveq-core` | production |
| `pypi-moveq-catalogue` | `moveq-catalogue` | production |
| `pypi-moveq-cli` | `moveq-cli` | production |
| `testpypi-moveq` | `moveq` | TestPyPI |
| `testpypi-moveq-core` | `moveq-core` | TestPyPI |
| `testpypi-moveq-catalogue` | `moveq-catalogue` | TestPyPI |
| `testpypi-moveq-cli` | `moveq-cli` | TestPyPI |

Do **not** reuse a single environment named `pypi` or `testpypi` for all four.

Required reviewers on the `pypi-*` environments are recommended once you have
a collaborator who can approve. A solo maintainer cannot require self-review.
Do **not** enable "Prevent self-review" on a one-person project or you will be
unable to publish.

### 3. Pending publishers on PyPI (wave 1: three names)

PyPI rejects a fourth pending publisher:

> You can't register more than 3 pending trusted publishers at once.

Open <https://pypi.org/manage/account/publishing/> and register **only these
three** (you may already have them):

| PyPI project name | Owner | Repository | Workflow | Environment name |
| --- | --- | --- | --- | --- |
| `moveq` | `SVamseekar` | `moveq` | `publish.yml` | `pypi-moveq` |
| `moveq-core` | `SVamseekar` | `moveq` | `publish.yml` | `pypi-moveq-core` |
| `moveq-catalogue` | `SVamseekar` | `moveq` | `publish.yml` | `pypi-moveq-catalogue` |

Leave `moveq-cli` until wave 2. The workflow name is the **filename only**,
not `.github/workflows/publish.yml`.

The first successful upload creates the project. That pending publisher then
becomes an ordinary publisher on the project, which frees a pending slot.

### 4. Pending publishers on TestPyPI (wave 1: same three)

Open <https://test.pypi.org/manage/account/publishing/>. Register at most
three, matching production:

| Project name | Owner | Repository | Workflow | Environment name |
| --- | --- | --- | --- | --- |
| `moveq` | `SVamseekar` | `moveq` | `publish.yml` | `testpypi-moveq` |
| `moveq-core` | `SVamseekar` | `moveq` | `publish.yml` | `testpypi-moveq-core` |
| `moveq-catalogue` | `SVamseekar` | `moveq` | `publish.yml` | `testpypi-moveq-catalogue` |

### 5. What not to create

- Do **not** add `PYPI_API_TOKEN` or `TEST_PYPI_API_TOKEN` GitHub secrets.
- Do **not** put a PyPI token in `~/.pypirc` for production releases.
- Do **not** run `twine upload` to production PyPI from your laptop.

A TestPyPI API token is acceptable only as an emergency fallback. Prefer OIDC.

## Local validation (optional, no upload)

From the repository root, with the dev environment activated:

```bash
python -m pip install --upgrade build twine
python scripts/check_release_version.py
python scripts/build_dists.py
python -m twine check --strict dist/*/*
```

Install a wheel in a **clean** virtualenv to see what users will get:

```bash
python -m venv /tmp/moveq-wheel-check
source /tmp/moveq-wheel-check/bin/activate
python -m pip install dist/moveq/*.whl
python -c "import moveq; print(moveq.__version__, moveq.compute_gini)"
```

`dist/` is generated output and is gitignored. Do not commit it.

`moveq` and `moveq-cli` wheels depend on the sibling packages. A clean
`pip install dist/moveq-*.whl` talks to PyPI for `moveq-core` and
`moveq-catalogue`. Before those exist on PyPI, install the local wheels in
dependency order:

```bash
python -m pip install dist/moveq-core/*.whl dist/moveq-catalogue/*.whl
python -m pip install dist/moveq/*.whl
python -m pip install dist/moveq-cli/*.whl
```

## TestPyPI dry run

Two waves, because of the three-pending-publisher cap.

**Wave 1** — `moveq`, `moveq-core`, `moveq-catalogue` pending on TestPyPI.

1. Push `main` so `.github/workflows/publish.yml` exists on GitHub.
2. GitHub → **Actions** → **Publish** → **Run workflow**.
3. The three registered packages upload. `moveq-cli` is expected to **fail**
   (no pending publisher yet). That is OK (`fail-fast: false`).
4. Confirm the three TestPyPI project pages.

**Wave 2** — add `moveq-cli`:

| Project name | Environment name |
| --- | --- |
| `moveq-cli` | `testpypi-moveq-cli` |

5. Re-run the failed jobs (or run the workflow again). `skip-existing: true`
   skips the three packages already on TestPyPI.
6. Confirm `https://test.pypi.org/project/moveq-cli/`.

The workflow tests, builds, and uploads to TestPyPI. It does **not**
create a GitHub Release and does **not** upload to production PyPI.

After both waves, install and check:

```bash
python -m venv /tmp/moveq-testpypi
source /tmp/moveq-testpypi/bin/activate
python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  moveq moveq-cli
python -c "import moveq; print(moveq.__version__)"
moveq --help
```

`--extra-index-url` is required because TestPyPI does not host NumPy. Open
each TestPyPI project page and confirm the README, license, and project URLs
render.

TestPyPI **does not allow reusing a version**. If you need another dry run of
the same code, bump to a local/dev version such as `0.1.0rc1` in all four
files, or wait until the next real version. `skip-existing: true` only skips
files that already exist; it cannot replace them.

## Production release

1. Tests on `main` are green.
2. Set `version = "X.Y.Z"` in all four `pyproject.toml` files.
3. Move notes in `CHANGELOG.md` from **Unreleased** into `## [X.Y.Z] — YYYY-MM-DD`.
4. Commit and push `main`:

   ```bash
   git add -u
   git commit -m "chore: release vX.Y.Z"
   git push origin main
   ```

5. Tag the **same** commit (annotated tag):

   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

6. Watch **Actions → Publish**. The first run publishes the three names that
   already have pending publishers. `moveq-cli` fails until you add it.

   After those three projects exist on PyPI, add the fourth pending publisher:

   | PyPI project name | Environment name |
   | --- | --- |
   | `moveq-cli` | `pypi-moveq-cli` |

   Then **Re-run all jobs** on that tag workflow (`skip-existing` protects the
   first three). On success:
   - all four projects appear on PyPI
   - a GitHub Release named `vX.Y.Z` is created with the wheels and sdists
     attached
7. Verify from a clean environment:

   ```bash
   python -m pip install moveq moveq-cli
   python -c "import moveq; print(moveq.__version__)"
   ```

PyPI versions are immutable. A broken `X.Y.Z` is fixed by publishing
`X.Y.Z+1` (usually a patch). You may [yank](https://pypi.org/help/#yanked) a
bad version so new installs skip it; yanking does not delete files already
downloaded.

## Workflow behaviour

File: [`.github/workflows/publish.yml`](../.github/workflows/publish.yml)

| Trigger | Tests | Build | PyPI | TestPyPI | GitHub Release |
| --- | --- | --- | --- | --- | --- |
| Push tag `v*` | yes | yes | yes | no | yes |
| `workflow_dispatch` | yes | yes | no | yes | no |
| Push / PR to `main` | [ci.yml](../.github/workflows/ci.yml) only | check only | no | no | no |

The publish job uses `permissions: id-token: write` so GitHub can mint a
short-lived OIDC token. PyPI exchanges that token for a one-time upload
credential. The `pypa/gh-action-pypi-publish` action also generates
[PEP 740](https://peps.python.org/pep-0740/) attestations by default.

Build and publish are **separate jobs**. The publish job only downloads the
already-built artifacts. That is required by PyPA's Trusted Publishing guide.

## GitHub settings to keep

These match GitHub's recommended defaults for a public library:

- Default branch: `main`
- Actions: allow GitHub-hosted runners; restrict third-party actions if you
  later need a tighter allow-list. `pypa/gh-action-pypi-publish` must remain
  allowed.
- Dependabot: enabled for `github-actions` (see `.github/dependabot.yml`)
- Private vulnerability reporting: enabled (see [SECURITY.md](../SECURITY.md))
- Delete head branches on merge: enabled
- Do not grant `id-token: write` or `contents: write` at the workflow level
  globally. Those permissions stay on the individual publish / release jobs.

Recommended later, when there is more than one maintainer:

- Branch protection on `main`: require the CI workflow, disallow force pushes
- Required reviewers on the `pypi-*` environments

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| `You can't register more than 3 pending trusted publishers at once` | Account limit. Keep three pending, publish them, then add `moveq-cli` |
| `A pending trusted publisher matching this configuration has already been registered for a different project name` | Two pending publishers share the same `(repo, publish.yml, environment)`. Each package needs its own `pypi-<name>` environment |
| `Trusted publishing exchange failure` | Pending publisher fields do not match: owner, repo, `publish.yml`, or environment name |
| `Project already exists` on first upload | Someone else owns the name, or you created the project manually without adding this workflow as a publisher |
| Version check fails | Tag `v0.1.0` but a `pyproject.toml` still says `0.1.0` vs `0.2.0` (not lockstep) |
| TestPyPI 400 "file already exists" | That version was already uploaded; bump the version |
| `pip install moveq` cannot find `moveq-core` | Core was not published, or PyPI index lag of a few minutes |
| GitHub Release step fails after PyPI succeeded | Re-run only the release job, or `gh release create` manually; do not retag the same version |

## References

- [PyPA: publishing with GitHub Actions](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [Making a PyPI-friendly README](https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
