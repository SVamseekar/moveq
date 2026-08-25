"""moveq — umbrella package over moveq-core and moveq-catalogue."""

from moveq_catalogue import Catalogue, SectionAction, SectionMapping
from moveq_core import (
    ScoreComponent,
    ScoreResult,
    clip01,
    compute_concentration_index,
    compute_gini,
    compute_palma_ratio,
    compute_score,
)

__all__ = [
    "compute_gini",
    "compute_palma_ratio",
    "compute_concentration_index",
    "compute_score",
    "clip01",
    "ScoreComponent",
    "ScoreResult",
    "Catalogue",
    "SectionAction",
    "SectionMapping",
]

__version__ = "0.1.1"
