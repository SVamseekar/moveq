"""Configurable weighted composite score (0-100) with graceful missing-term handling.

The pattern: define named terms in [0, 1], each with a design weight. Score
is ``100 * sum(weight * value)``. If a term is missing (``None``), it is
dropped and the remaining weights are renormalised — the score never
silently treats a missing input as zero.

Unlike a fixed formula, weights and labels are supplied by the caller, so
the same engine works for any composite indicator (a bus-access score, a
walkability score, a service-quality score, ...).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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


@dataclass(frozen=True)
class ScoreResult:
    score: float | None
    components: list[ScoreComponent]
    dropped: list[str]
    n_areas: int | None
    note: str | None
    context: dict[str, str] = field(default_factory=dict)

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
        }


def compute_score(
    terms: dict[str, float | None],
    weights: dict[str, float],
    *,
    labels: dict[str, str] | None = None,
    n_areas: int | None = None,
    context: dict[str, str] | None = None,
    empty_note: str = "No score for this cut — required inputs are missing.",
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
        empty_note: Note returned when every term is missing.
    """
    labels = labels or {k: k for k in weights}
    context = context or {}

    present: list[tuple[str, float, float]] = []
    dropped: list[str] = []
    for key, design_w in weights.items():
        raw = terms.get(key)
        if raw is None:
            dropped.append(key)
            continue
        present.append((key, design_w, clip01(raw)))

    if not present:
        components = [
            ScoreComponent(
                id=k, label=labels.get(k, k), design_weight=w, weight_used=0.0, value=None, missing=True
            )
            for k, w in weights.items()
        ]
        return ScoreResult(
            score=None,
            components=components,
            dropped=list(weights),
            n_areas=n_areas or 0,
            note=empty_note,
            context=context,
        )

    weight_sum = sum(w for _, w, _ in present)
    components = []
    weighted = 0.0
    present_ids = {k for k, _, _ in present}
    for key, design_w in weights.items():
        if key not in present_ids:
            components.append(
                ScoreComponent(
                    id=key, label=labels.get(key, key), design_weight=design_w,
                    weight_used=0.0, value=None, missing=True,
                )
            )
            continue
        value = next(v for k, _, v in present if k == key)
        used = design_w / weight_sum
        weighted += used * value
        components.append(
            ScoreComponent(
                id=key, label=labels.get(key, key), design_weight=design_w,
                weight_used=used, value=value, missing=False,
            )
        )

    note = None
    if dropped:
        dropped_labels = ", ".join(labels.get(k, k).split(" (")[0].lower() for k in dropped)
        note = f"{dropped_labels} not in this cut — weights renormalised."

    return ScoreResult(
        score=100.0 * weighted,
        components=components,
        dropped=dropped,
        n_areas=n_areas,
        note=note,
        context=context,
    )
