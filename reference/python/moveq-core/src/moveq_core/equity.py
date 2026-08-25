"""Population-weighted inequality measures for transport-equity analysis.

Three measures, one shared idea: service is a resource, population is the
weight, and we ask how unevenly the resource is spread across the weight.

    Gini                 — overall inequality via the Lorenz curve, in [0, 1]
    Palma ratio          — top-10% mean service / bottom-40% mean service
    Concentration Index  — inequality correlated with a rank (e.g. deprivation);
                            positive = pro-rich, negative = pro-poor

NumPy 2.x guard: uses ``trapezoid`` with a fallback to the removed ``trapz``.
"""

from __future__ import annotations

import numpy as np

_trapezoid = getattr(np, "trapezoid", getattr(np, "trapz", None))
if _trapezoid is None:
    raise ImportError("NumPy has neither 'trapezoid' nor 'trapz' — unsupported version")


def _as_1d(name: str, x: object) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be a 1-dimensional array")
    return arr


def _validate_weighted_input(
    values: np.ndarray,
    weights: np.ndarray,
    *,
    values_name: str = "values",
    weights_name: str = "weights",
    allow_negative_values: bool = False,
) -> None:
    if values.shape != weights.shape:
        raise ValueError(f"{values_name} and {weights_name} must have the same length")
    if values.size == 0:
        raise ValueError(f"{values_name} and {weights_name} must not be empty")
    if not np.all(np.isfinite(values)):
        raise ValueError(f"{values_name} must be finite")
    if not np.all(np.isfinite(weights)):
        raise ValueError(f"{weights_name} must be finite")
    if np.any(weights < 0):
        raise ValueError(f"{weights_name} must be non-negative")
    if weights.sum() <= 0:
        raise ValueError(f"total {weights_name} must be positive")
    if not allow_negative_values and np.any(values < 0):
        raise ValueError(f"{values_name} must be non-negative")


def _prepare_weighted(
    values: object,
    weights: object,
    *,
    values_name: str = "values",
    weights_name: str = "weights",
    allow_negative_values: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    values_arr = _as_1d(values_name, values)
    weights_arr = _as_1d(weights_name, weights)
    _validate_weighted_input(
        values_arr,
        weights_arr,
        values_name=values_name,
        weights_name=weights_name,
        allow_negative_values=allow_negative_values,
    )
    return values_arr, weights_arr


def compute_gini(values: np.ndarray, weights: np.ndarray) -> float:
    """Population-weighted Gini coefficient via Lorenz curve area.

    Args:
        values: Service level per areal unit (e.g. trips per neighbourhood).
        weights: Population weight per unit.

    Returns:
        Gini coefficient in [0, 1]. 0 = perfect equality, 1 = maximum
        inequality. By convention, zero total service (nothing to
        distribute) is treated as perfect equality and returns 0.0.
    """
    values, weights = _prepare_weighted(values, weights)

    total_service = (values * weights).sum()
    if total_service == 0:
        return 0.0

    order = np.argsort(values, kind="stable")
    values = values[order]
    weights = weights[order]

    cum_pop = np.cumsum(weights) / weights.sum()
    cum_service = np.cumsum(values * weights) / total_service

    cum_pop = np.concatenate([[0], cum_pop])
    cum_service = np.concatenate([[0], cum_service])

    lorenz_area = _trapezoid(cum_service, cum_pop)
    return float(1 - 2 * lorenz_area)


def compute_palma_ratio(values: np.ndarray, weights: np.ndarray) -> float:
    """Palma ratio: mean service in the top 10% / mean service in the bottom 40%.

    Areas whose population straddles the 40%/90% cumulative-population cuts
    are split proportionally, so the result doesn't depend on how finely the
    input is divided into areas or on tie ordering.

    Args:
        values: Service level per areal unit.
        weights: Population weight per unit.

    Returns:
        Palma ratio. Higher = more unequal. Equal service (including the
        all-zero convention) returns ``1.0``. ``inf`` if the bottom 40% has
        zero mean service while the top 10% does not.
    """
    values, weights = _prepare_weighted(values, weights)

    order = np.argsort(values, kind="stable")
    values = values[order]
    weights = weights[order]

    total = weights.sum()
    cum_weight = np.cumsum(weights)
    cum_before = cum_weight - weights

    bottom_cut = 0.40 * total
    top_cut = 0.90 * total

    bottom_overlap = np.clip(np.minimum(cum_weight, bottom_cut) - cum_before, 0, None)
    top_overlap = np.clip(cum_weight - np.maximum(cum_before, top_cut), 0, None)

    bottom_weight = bottom_overlap.sum()
    top_weight = top_overlap.sum()

    bottom_mean = float(np.sum(values * bottom_overlap) / bottom_weight) if bottom_weight > 0 else 0.0
    top_mean = float(np.sum(values * top_overlap) / top_weight) if top_weight > 0 else 0.0

    if bottom_mean == 0.0 and top_mean == 0.0:
        return 1.0
    return float(top_mean / bottom_mean) if bottom_mean > 0 else float("inf")


def compute_concentration_index(
    service: np.ndarray, rank: np.ndarray, population: np.ndarray
) -> float:
    """Wagstaff Concentration Index (CI) via the covariance method.

    Positive CI = service concentrated in areas with a higher rank value
    (e.g. less deprived, if rank is a deprivation rank). Negative CI = service
    concentrated in lower-rank (e.g. more deprived) areas.

    Units that tie on ``rank`` share the population-weighted average
    fractional rank of their tied group, so the result doesn't depend on
    the arbitrary order ties happen to appear in.

    Args:
        service: Service level per areal unit.
        rank: Ranking variable per unit (e.g. deprivation rank; 1 = most
            deprived, higher = less deprived).
        population: Population weight per unit.

    Returns:
        Concentration Index. For non-negative service this lies in [-1, 1].
        Zero mean service returns ``0.0``.
    """
    service, population = _prepare_weighted(
        service, population, values_name="service", weights_name="population", allow_negative_values=True
    )
    rank = _as_1d("rank", rank)
    if rank.shape != service.shape:
        raise ValueError("rank must have the same length as service")
    if not np.all(np.isfinite(rank)):
        raise ValueError("rank must be finite")

    live = population > 0
    if not np.all(live):
        service = service[live]
        rank = rank[live]
        population = population[live]

    total_pop = population.sum()
    order = np.argsort(rank, kind="stable")
    rank_sorted = rank[order]
    pop_sorted = population[order]
    service_sorted = service[order]

    # Tied ranks share the group's population-weighted midpoint fractional rank,
    # i.e. (mass before the group + half the group's mass) / total population.
    starts = np.empty(rank_sorted.size, dtype=bool)
    starts[0] = True
    starts[1:] = rank_sorted[1:] != rank_sorted[:-1]
    group_id = np.cumsum(starts) - 1
    n_groups = int(group_id[-1]) + 1
    group_pop = np.bincount(group_id, weights=pop_sorted, minlength=n_groups)
    group_before = np.cumsum(group_pop) - group_pop
    frac_rank = (group_before + 0.5 * group_pop)[group_id] / total_pop

    mean_service = float(np.average(service_sorted, weights=pop_sorted))
    if mean_service == 0.0:
        return 0.0
    cov = float(
        np.average((service_sorted - mean_service) * (frac_rank - 0.5), weights=pop_sorted)
    )
    return float(2 * cov / mean_service)
