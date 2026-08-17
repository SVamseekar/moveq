"""moveq-core — pure algorithms for transport-equity analysis."""

from moveq_core.equity import compute_concentration_index, compute_gini, compute_palma_ratio
from moveq_core.score import ScoreComponent, ScoreResult, clip01, compute_score

__all__ = [
    "compute_gini",
    "compute_palma_ratio",
    "compute_concentration_index",
    "compute_score",
    "clip01",
    "ScoreComponent",
    "ScoreResult",
]

__version__ = "0.1.0"
