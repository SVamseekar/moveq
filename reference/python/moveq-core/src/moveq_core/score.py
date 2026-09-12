"""Configurable weighted composite score (0-100) with declared missing-term policy.

The pattern: define named terms in [0, 1], each with a design weight. Score
is ``100 * sum(weight * value)``. When a term is missing (``None``), the
caller names a policy: renormalise remaining weights (``reweight``, today's
default), treat missing as zero (``as_zero``), refuse a score (``exclude``),
or return best/worst-case bounds (``bounds``). None of these is inherently
correct; they answer different questions.

Unlike a fixed formula, weights and labels are supplied by the caller, so
the same engine works for any composite indicator (a bus-access score, a
walkability score, a service-quality score, ...).
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass, field
from typing import Any, Literal


def clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class ScoreComponent:
    id: str
    label: str
    design_weight: float
    weight_used: float
    value: float | None
    missing: bool


MissingPolicy = Literal["reweight", "as_zero", "exclude", "bounds"]
_MISSING_POLICIES = ("reweight", "as_zero", "exclude", "bounds")


@dataclass(frozen=True)
class ScoreResult:
    score: float | None
    components: list[ScoreComponent]
    dropped: list[str]
    n_areas: int | None
    note: str | None
    context: dict[str, str] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    bounds: tuple[float, float] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": None if self.score is None else round(self.score, 1),
            "components": [
                {
                    "id": c.id,
                    "label": c.label,
                    "design_weight": c.design_weight,
                    "weight_used": c.weight_used,
                    "value": None if c.value is None else round(c.value, 4),
                    "missing": c.missing,
                }
                for c in self.components
            ],
            "dropped": list(self.dropped),
            "n_areas": self.n_areas,
            "note": self.note,
            "context": dict(self.context),
            "parameters": dict(self.parameters),
            "bounds": None if self.bounds is None else [self.bounds[0], self.bounds[1]],
        }


def _resolve_missing_policy(missing_policy: MissingPolicy | None) -> MissingPolicy:
    if missing_policy is None:
        warnings.warn(
            "missing_policy omitted; recorded as 'reweight'",
            UserWarning,
            stacklevel=3,
        )
        return "reweight"
    if missing_policy not in _MISSING_POLICIES:
        raise ValueError(
            "missing_policy must be one of 'reweight', 'as_zero', 'exclude', or 'bounds'"
        )
    return missing_policy


def _dropped_labels(dropped: list[str], labels: dict[str, str]) -> str:
    return ", ".join(labels.get(k, k).split(" (")[0].lower() for k in dropped)


def compute_score(
    terms: dict[str, float | None],
    weights: dict[str, float],
    *,
    labels: dict[str, str] | None = None,
    n_areas: int | None = None,
    context: dict[str, str] | None = None,
    empty_note: str = "No score for this cut — required inputs are missing.",
    missing_policy: MissingPolicy | None = None,
) -> ScoreResult:
    """Compute a weighted composite score from 0-1 terms (``None`` = missing).

    Args:
        terms: Mapping of term id to a value in [0, 1], or ``None`` if the
            term has no data for this cut.
        weights: Mapping of term id to its design weight. Keys must be a
            superset of ``terms``' keys that matter to the score.
        labels: Optional human-readable label per term id, used in notes.
        n_areas: Optional count of areal units backing this score.
        context: Optional free-form context (e.g. region, filter) carried
            through to the result for traceability.
        empty_note: Note returned when every term is missing under
            ``reweight`` / ``exclude``.
        missing_policy: ``reweight`` (default, today's arithmetic),
            ``as_zero``, ``exclude``, or ``bounds``. Omission is recorded
            as ``reweight`` and emits a warning.
    """
    labels = labels or {k: k for k in weights}
    context = context or {}
    policy = _resolve_missing_policy(missing_policy)
    parameters: dict[str, Any] = {"missing_policy": policy}

    for key, design_w in weights.items():
        if not math.isfinite(design_w) or design_w <= 0:
            raise ValueError(f"weight for {key!r} must be finite and strictly positive, got {design_w}")

    present: list[tuple[str, float, float]] = []
    dropped: list[str] = []
    for key, design_w in weights.items():
        raw = terms.get(key)
        if raw is None:
            dropped.append(key)
            continue
        value = float(raw)
        if not math.isfinite(value):
            raise ValueError(f"term {key!r} must be finite, got {raw}")
        present.append((key, design_w, clip01(value)))

    def _all_missing_components() -> list[ScoreComponent]:
        return [
            ScoreComponent(
                id=k, label=labels.get(k, k), design_weight=w, weight_used=0.0, value=None, missing=True
            )
            for k, w in weights.items()
        ]

    if not present:
        if policy == "as_zero":
            total_w = sum(weights.values())
            components = [
                ScoreComponent(
                    id=k, label=labels.get(k, k), design_weight=w,
                    weight_used=w / total_w, value=0.0, missing=True,
                )
                for k, w in weights.items()
            ]
            note = (
                f"{_dropped_labels(list(weights), labels)} missing — treated as zero "
                f"(missing_policy='as_zero')."
            )
            return ScoreResult(
                score=0.0,
                components=components,
                dropped=list(weights),
                n_areas=n_areas,
                note=note,
                context=context,
                parameters=parameters,
                bounds=None,
            )
        if policy == "bounds":
            note = (
                f"{_dropped_labels(list(weights), labels)} missing — no point score; "
                f"bounds are best- and worst-case over missing terms "
                f"(missing_policy='bounds')."
            )
            return ScoreResult(
                score=None,
                components=_all_missing_components(),
                dropped=list(weights),
                n_areas=n_areas,
                note=note,
                context=context,
                parameters=parameters,
                bounds=(0.0, 100.0),
            )
        note = empty_note if policy == "reweight" else (
            f"{_dropped_labels(list(weights), labels)} missing — no score returned "
            f"(missing_policy='exclude')."
        )
        return ScoreResult(
            score=None,
            components=_all_missing_components(),
            dropped=list(weights),
            n_areas=n_areas,
            note=note,
            context=context,
            parameters=parameters,
            bounds=None,
        )

    present_values = {k: v for k, _, v in present}
    total_design = sum(weights.values())
    present_weight_sum = sum(w for _, w, _ in present)

    def _used_weight(design_w: float, *, missing: bool) -> float:
        if policy == "reweight":
            return 0.0 if missing else design_w / present_weight_sum
        return design_w / total_design

    def _point_score(*, fill_missing: float) -> float:
        weighted = 0.0
        for key, design_w in weights.items():
            if key in present_values:
                y = present_values[key]
            elif policy == "reweight":
                continue
            else:
                y = fill_missing
            weighted += _used_weight(design_w, missing=key not in present_values) * y
        return 100.0 * weighted

    components = []
    for key, design_w in weights.items():
        missing = key not in present_values
        if missing:
            shown = 0.0 if policy == "as_zero" else None
            components.append(
                ScoreComponent(
                    id=key, label=labels.get(key, key), design_weight=design_w,
                    weight_used=_used_weight(design_w, missing=True),
                    value=shown, missing=True,
                )
            )
            continue
        value = present_values[key]
        components.append(
            ScoreComponent(
                id=key, label=labels.get(key, key), design_weight=design_w,
                weight_used=_used_weight(design_w, missing=False),
                value=value, missing=False,
            )
        )

    dropped_text = _dropped_labels(dropped, labels) if dropped else ""

    if policy == "exclude" and dropped:
        note = (
            f"{dropped_text} missing — no score returned (missing_policy='exclude')."
        )
        return ScoreResult(
            score=None,
            components=components,
            dropped=dropped,
            n_areas=n_areas,
            note=note,
            context=context,
            parameters=parameters,
            bounds=None,
        )

    if policy == "bounds":
        if not dropped:
            score = _point_score(fill_missing=0.0)
            return ScoreResult(
                score=score,
                components=components,
                dropped=dropped,
                n_areas=n_areas,
                note=None,
                context=context,
                parameters=parameters,
                bounds=(score, score),
            )
        low = _point_score(fill_missing=0.0)
        high = _point_score(fill_missing=1.0)
        note = (
            f"{dropped_text} missing — no point score; bounds are best- and "
            f"worst-case over missing terms (missing_policy='bounds')."
        )
        return ScoreResult(
            score=None,
            components=components,
            dropped=dropped,
            n_areas=n_areas,
            note=note,
            context=context,
            parameters=parameters,
            bounds=(low, high),
        )

    score = _point_score(fill_missing=0.0)
    note = None
    if dropped and policy == "reweight":
        note = f"{dropped_text} not in this cut — weights renormalised."
    elif dropped and policy == "as_zero":
        note = f"{dropped_text} missing — treated as zero (missing_policy='as_zero')."

    return ScoreResult(
        score=score,
        components=components,
        dropped=dropped,
        n_areas=n_areas,
        note=note,
        context=context,
        parameters=parameters,
        bounds=None,
    )
