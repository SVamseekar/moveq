# CLAUDE.md — working agreement for moveq

Read this before any change. It points at the authoritative files rather than
repeating them, because duplicated policy drifts and then contradicts.

| Topic | Source of truth |
| --- | --- |
| Versioning policy | [CONTRIBUTING.md](CONTRIBUTING.md) § Versioning |
| Agent rules | [AGENTS.md](AGENTS.md) |
| Release / PyPI procedure | [docs/publishing.md](docs/publishing.md) |
| Bump anti-rationalisation | `.grok/skills/moveq-versioning/SKILL.md` |

If this file disagrees with any of the above, **those win** — and fix this file.

---

## 1. The rule agents break most often

> **Commits are not releases.**

Do **not** edit `version` in any `pyproject.toml`, do **not** edit `__version__`
in any `__init__.py`, and do **not** create a git tag — unless the user has
explicitly asked to publish.

A finished work slice is ordinary commits. The version stays at the last
released number until a release is requested. This is enforced three ways:

- CI job **Git release rules** → `python scripts/check_release_version.py --git-rules`
- Pre-push hook → `scripts/git-hooks/pre-push` (install: `git config core.hooksPath scripts/git-hooks`)
- Publish workflow → **every `v*` tag is a PyPI upload**

Never bypass with `--no-verify`.

---

## 2. Versioning: scientific Python, not Cargo

moveq follows [SemVer](https://semver.org/) as **NumPy, SciPy, scikit-learn and
statsmodels** interpret it — *not* Cargo's pre-1.0 convention where the middle
number is the breaking channel.

| Change | Bump | Example |
| --- | --- | --- |
| Bug fix, **including numerical/correctness fixes that change outputs** | **patch** | `0.1.1` → `0.1.2` |
| Docs, tests, packaging only | **patch** | `0.1.1` → `0.1.2` |
| New backwards-compatible public API | **minor** | `0.1.2` → `0.2.0` |
| Breaking public API (rename/remove/change signature) while `0.x` | **minor** | `0.1.2` → `0.2.0` |
| Intentional *redefinition* of a metric | **minor** | `0.1.2` → `0.2.0` |
| Breaking public API after `1.0.0` | **major** | `1.2.0` → `2.0.0` |

**Why patch for correctness fixes.** `pip install "moveq~=0.1.1"` resolves to
`>=0.1.1, ==0.1.*`. A correctness fix shipped as `0.2.0` **never reaches those
users**. scikit-learn `0.24.1` shipped a numerical stability fix in
`mutual_info_score` as a patch. Do the same.

If a patch changes numeric results, say so in `CHANGELOG.md` **under that
patch**, so anyone re-running a study knows to expect different figures.

Do not declare `1.0.0` until the public API is intentionally stable.

### Rationalisations that are wrong

| Excuse | Reality |
| --- | --- |
| "The number changed, so it's breaking → minor" | Output matching the documented definition is a bug fix. Patch. |
| "We're 0.x, so every behaviour change is 0.2.0" | That's Cargo. This repo patches on `0.x`. |
| "Safer to bump minor so people notice" | The changelog records it. Still a patch. |
| "This slice is the 0.2 / trust release" | Tests and docs are a **patch** when released. Leave the version alone until publish is requested. |
| "Tag every finished slice so history is clear" | Tags are PyPI releases. Commits document work. |

---

## 3. Tagging contract

**Form.** `vX.Y.Z` — lowercase `v`, no suffix, no `release-` prefix.

**Annotated, never lightweight.** Every existing tag is a real tag object
(`git for-each-ref refs/tags --format='%(refname:short) %(objecttype)'` →
`tag`). Annotated tags carry a tagger, date and message, and are what
`git describe` and provenance tooling expect.

```bash
git tag -a v0.2.0 -m "moveq 0.2.0"
```

**Lockstep.** One tag publishes **four** PyPI projects — `moveq`, `moveq-core`,
`moveq-catalogue`, `moveq-cli`. The tag without its `v` must equal `version` in
all four `pyproject.toml` files **and** `__version__` in all four
`__init__.py` files. `check_release_version.py` fails the publish otherwise.

**Never tag a feature commit.** Tag only the release commit — the one whose
`CHANGELOG.md` carries the `## [X.Y.Z]` heading.

**Tags are immutable.** Never move, delete or re-point a pushed tag: PyPI
rejects re-uploads of an existing version, and consumers pin to tags. A bad
release is superseded by the next patch, never rewritten.

### Release sequence

```bash
# 1. Bump all 8 files (4 pyproject.toml + 4 __init__.py) in ONE commit
# 2. CHANGELOG.md gains "## [X.Y.Z] - YYYY-MM-DD"
# 3. Verify before tagging
python scripts/check_release_version.py X.Y.Z
python scripts/check_release_version.py --git-rules
pytest -v

# 4. Commit, tag, push
git commit -am "release: vX.Y.Z"
git tag -a vX.Y.Z -m "moveq X.Y.Z"
git push origin main
git push origin vX.Y.Z          # ← this triggers the PyPI publish
```

Push the branch **before** the tag, so CI validates the release commit first.

**Never put a production PyPI token on a laptop or in repo secrets.** Releases
use [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) with
per-package GitHub Environments. See `docs/publishing.md`.

---

## 4. Changelog

[Keep a Changelog](https://keepachangelog.com/) format, already in use.

- Heading `## [X.Y.Z] — YYYY-MM-DD` (em dash, matching existing entries). The
  release gate requires `^## \[X.Y.Z\]` followed by whitespace; the date and its
  separator are free-form, but stay consistent with the entries already there.
- Group under `Added` / `Changed` / `Fixed` / `Removed` / `Deprecated`
- **If numeric outputs change, state it explicitly under that version**
- Breaking changes get a migration note showing before → after

---

## 5. Commits

**Match the existing history — do not introduce a new convention.**

`git log` shows a Conventional-Commits style already in consistent use. The
types observed in this repo are:

```
feat:   fix:   docs:   test:   ci:   chore:
```

Before writing a commit message, read recent history (`git log --oneline -20`)
and match it. Do not invent additional types, and do not restyle existing
practice.

The same applies to prose in commits, PRs, issues, docs and the website: this
repository has its own established voice and spelling (predominantly British
`-ise` / `-isation` in prose; existing API identifiers such as
`harmonization` keep their spelling). Follow what is already there rather than
imposing a house style from elsewhere.

---

## 6. Branching and PRs

- Work on a branch; do not commit directly to `main`
- One logical change per PR; keep them reviewable
- CI must be green: tests on all supported Pythons, website check, git release rules
- Do not bump versions in feature PRs (§1)

---

## 7. Metric tests — non-negotiable

From `AGENTS.md`, restated because it is easy to get wrong:

- Expected values must come from an **independent second implementation** of the
  documented formula, or a closed-form case — **never** from calling the
  production function
- **Do not** use an external statistics library as an oracle; their conventions
  differ (tie handling, rank direction, normalisation)
- Property tests are **required** for metric changes: permutation invariance,
  scale invariance, documented bounds, tie handling
- Test the edges: zero population, zero mean, near-zero mean (cancellation),
  single unit, all-equal values

---

## 8. Scientific-credibility order

Do not skip ahead unless asked:

1. Independent verification of Gini, Palma, CI and score
2. Auditable result objects for the equity metrics
3. Research reproductions of published statistics
4. Interop **after** GTFS/accessibility tools — not a GTFS parser

---

## 9. Claims discipline

moveq's credibility is the product. Applies to code, docs, website and specs.

- **Never document behaviour that isn't implemented.** If the docs say a
  capability exists, it must exist in the source and be tested.
- **Never state a legal or regulatory threshold** as if a computed value
  triggers it. moveq generates evidence; it does not determine compliance.
- **Never claim uniqueness.** Gini and concentration indices are standard and
  well implemented elsewhere (`rineq`, WHO HEAT). moveq's contribution is
  explicit assumptions and reproducibility, not the formulas.
- **Describe concentration neutrally.** Use *advantage-concentrated* and
  *disadvantage-concentrated*. Do not attach a fairness or benefit/burden
  reading unless the API models it explicitly.
- **Reproduction claims require published per-unit values, a stated formula and
  obtainable data.** Otherwise the claim is an extension, not a reproduction.

---

## 10. Leave alone unless asked

- `website/` — do not edit without an explicit request
- `examples/benchmark.py` — same
- Pushed tags — never (§3)
