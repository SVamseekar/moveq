---
name: moveq-versioning
description: >
  Use when choosing or applying a moveq version bump, tagging a release,
  deciding patch vs minor vs major (0.1.2 vs 0.2.0), calling a work slice a
  0.2 / trust / credibility release, creating a git tag, or when metric
  outputs (Gini, Palma, Concentration Index, compute_score) change after a
  bug fix.
---

# moveq versioning

Read **CONTRIBUTING.md § Versioning** before any bump. That file is the source
of truth. This skill stops the wrong bump *and* a bump that nobody asked for.

## When not to bump

Do not edit `version` / `__version__` or create a git tag unless the user
asked to publish. Commits are not releases. One Git tag publishes all four
packages. CI (`python scripts/check_release_version.py --git-rules`) rejects
a bump that is not a changelog release heading. Do not `--no-verify`.

## Rule

Scientific Python, not Cargo `0.x`. Apply this table only when a release
*was* requested.

| Situation | Bump |
| --- | --- |
| Formula/edge-case fix; numbers change; signatures do not | **patch** (`0.1.1` → `0.1.2`) |
| Docs, tests, or packaging only | **patch** |
| New public function or backwards-compatible API | **minor** |
| Rename/remove/change signatures (while `0.x`) | **minor** (`0.1.2` → `0.2.0`) |
| Intentional *redefinition* of a metric | **minor** |
| Same, after `1.0.0` | **major** |

`pip install "moveq~=0.1.1"` only receives `0.1.*`. Shipping a correctness fix
as `0.2.0` hides it from pinned users.

## Rationalizations that are wrong

| Excuse | Reality |
| --- | --- |
| "The number changed, so it is breaking → minor" | Output matching the documented definition is a bug fix (sklearn `0.24.1`). |
| "We are 0.x, so every behaviour change is 0.2.0" | That is Cargo. This repo patches on `0.x` like statsmodels / sklearn. |
| "Safer to bump minor so people notice" | Changelog records the numeric change; the bump is still patch. |
| "This slice is the 0.2 / trust release → minor now" | Tests and docs are a patch *when released*. New public API is a minor *when released*. Until the user asks to publish, leave the version alone. |
| "Tag every finished slice so history is clear" | Tags are PyPI releases. Commits document the work. |

If a patch changes published figures, write that in `CHANGELOG.md` under that
patch, then tag `vX.Y.Z` to match lockstep `pyproject.toml` versions
([docs/publishing.md](../../../docs/publishing.md)) — only as part of a
requested release.
