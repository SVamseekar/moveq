"""DataFrame convenience helpers. Requires the ``frames`` extra (pandas).

Kept separate from :mod:`moveq_core.equity` so the core numpy-only API has
no pandas dependency.
"""

from __future__ import annotations

try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "moveq_core.frames requires pandas — install with `pip install \"moveq-core[frames]\"`"
    ) from exc


def compute_vulnerability_index(df: "pd.DataFrame", factors: list[str]) -> "pd.Series":
    """Equal-weighted 0-100 vulnerability index across the given factor columns.

    Each factor is min-max normalised to 0-100 before averaging, so factors
    on different scales (a score, a percentage, a rate) contribute equally.

    Args:
        df: Frame containing the factor columns.
        factors: Column names to combine (e.g. deprivation score, no-car %,
            elderly %, disability %, unemployment rate).

    Returns:
        Series of vulnerability scores (0-100), rounded to 2 decimals.
    """
    normalised = pd.DataFrame(index=df.index)
    for col in factors:
        mn, mx = df[col].min(), df[col].max()
        normalised[col] = (df[col] - mn) / (mx - mn) * 100 if mx > mn else 0.0
    return normalised.mean(axis=1).round(2)


def identify_multiply_deprived(df: "pd.DataFrame", factors: list[str], min_factors: int = 3) -> "pd.Series":
    """Flag rows in the worst tertile on at least ``min_factors`` of the given factors.

    Args:
        df: Frame containing the factor columns.
        factors: Column names where a higher value means more deprived.
        min_factors: Minimum number of factors a row must be in the worst
            tertile on to be flagged.

    Returns:
        Boolean Series — True where the row is multiply-deprived.
    """
    worst_tertile = pd.DataFrame(index=df.index)
    for col in factors:
        threshold = df[col].quantile(2 / 3)
        worst_tertile[col] = df[col] >= threshold
    return worst_tertile.sum(axis=1) >= min_factors
