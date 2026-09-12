"""moveq — umbrella package over moveq-core and moveq-catalogue."""

from moveq_catalogue import Catalogue, SectionAction, SectionMapping
from moveq_core import (
    CLAIM_BADGES,
    PROMOTION_RULES,
    EquityResult,
    MoveqError,
    ScoreComponent,
    ScoreResult,
    UndefinedMetricError,
    ValidationIssue,
    ValidationReport,
    clip01,
    compute_concentration_index,
    compute_gini,
    compute_palma_ratio,
    compute_score,
    concentration_index_result,
    gini_result,
    palma_result,
    sha256_bytes,
    validate_descriptor,
    validate_registry,
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
    "CLAIM_BADGES",
    "PROMOTION_RULES",
    "ValidationIssue",
    "ValidationReport",
    "sha256_bytes",
    "validate_descriptor",
    "validate_registry",
]

__version__ = "0.2.0"
