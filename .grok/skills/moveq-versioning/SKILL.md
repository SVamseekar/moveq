---
name: moveq-versioning
description: >
  Use when choosing or applying a moveq version bump, tagging a release,
  deciding patch vs minor vs major (0.1.2 vs 0.2.0), or when metric outputs
  (Gini, Palma, Concentration Index, compute_score) change after a bug fix.
---

# moveq versioning

Read **CONTRIBUTING.md § Versioning** before any bump. That file is the source
of truth. This skill only stops the wrong bump.

## Rule

Scientific Python, not Cargo `0.x`.

| Situation | Bump |
| --- | --- |
| Formula/edge-case fix; numbers change; signatures do not | **patch** (`0.1.1` → `0.1.2`) |
| Docs or packaging only | **patch** |
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

If a patch changes published figures, write that in `CHANGELOG.md` under the
patch, then tag `vX.Y.Z` to match lockstep `pyproject.toml` versions
([docs/publishing.md](../../../docs/publishing.md)).
