"""moveq — umbrella package over moveq-core and moveq-catalogue."""

from moveq_catalogue import Catalogue, SectionAction, SectionMapping
from moveq_core import (
    EquityResult,
    MoveqError,
    ScoreComponent,
    ScoreResult,
    UndefinedMetricError,
    clip01,
    compute_concentration_index,
    compute_gini,
    compute_palma_ratio,
    compute_score,
    concentration_index_result,
    gini_result,
    palma_result,
)

__all__ = [
    "compute_gini",
    "compute_palma_ratio",
    "compute_concentration_index",
    "gini_result",
    "palma_result",
    "concentration_index_result",
    "EquityResult",
    "MoveqError",
    "UndefinedMetricError",
    "compute_score",
    "clip01",
    "ScoreComponent",
    "ScoreResult",
    "Catalogue",
    "SectionAction",
    "SectionMapping",
]

__version__ = "0.1.2"
