"""moveq-core — pure algorithms for transport-equity analysis."""

from moveq_core.equity import (
    EquityResult,
    MoveqError,
    UndefinedMetricError,
    compute_concentration_index,
    compute_gini,
    compute_palma_ratio,
    concentration_index_result,
    gini_result,
    palma_result,
)
from moveq_core.evidence import (
    CLAIM_BADGES,
    PROMOTION_RULES,
    ValidationIssue,
    ValidationReport,
    sha256_bytes,
    validate_descriptor,
    validate_registry,
)
from moveq_core.score import ScoreComponent, ScoreResult, clip01, compute_score

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
    "CLAIM_BADGES",
    "PROMOTION_RULES",
    "ValidationIssue",
    "ValidationReport",
    "sha256_bytes",
    "validate_descriptor",
    "validate_registry",
]

__version__ = "0.2.0"
