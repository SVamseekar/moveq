"""Population-weighted inequality measures for transport-equity analysis.

Three measures, one shared idea: service is a resource, population is the
weight, and we ask how unevenly the resource is spread across the weight.

    Gini                 — overall inequality via the Lorenz curve, in [0, 1]
    Palma ratio          — top-10% mean service / bottom-40% mean service
    Concentration Index  — inequality correlated with a rank (e.g. deprivation),
                            in [-1, 1]; positive = pro-rich, negative = pro-poor

NumPy 2.x guard: uses ``trapezoid`` with a fallback to the removed ``trapz``.
"""

from __future__ import annotations

import numpy as np

_trapezoid = getattr(np, "trapezoid", getattr(np, "trapz", None))
if _trapezoid is None:
    raise ImportError("NumPy has neither 'trapezoid' nor 'trapz' — unsupported version")


def compute_gini(values: np.ndarray, weights: np.ndarray) -> float:
    """Population-weighted Gini coefficient via Lorenz curve area.

    Args:
        values: Service level per areal unit (e.g. trips per neighbourhood).
        weights: Population weight per unit.

    Returns:
        Gini coefficient in [0, 1]. 0 = perfect equality, 1 = maximum inequality.
    """
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)

    order = np.argsort(values)
    values = values[order]
    weights = weights[order]

    cum_pop = np.cumsum(weights) / weights.sum()
    cum_service = np.cumsum(values * weights) / (values * weights).sum()

    cum_pop = np.concatenate([[0], cum_pop])
    cum_service = np.concatenate([[0], cum_service])

    lorenz_area = _trapezoid(cum_service, cum_pop)
    return float(1 - 2 * lorenz_area)


def compute_palma_ratio(values: np.ndarray, weights: np.ndarray) -> float:
    """Palma ratio: mean service in the top 10% / mean service in the bottom 40%.

    Args:
        values: Service level per areal unit.
        weights: Population weight per unit.

    Returns:
        Palma ratio. Higher = more unequal. ``inf`` if the bottom 40% has zero
        mean service.
    """
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)

    order = np.argsort(values)
    values = values[order]
    weights = weights[order]

    cum_pop_frac = np.cumsum(weights) / weights.sum()

    bottom_mask = cum_pop_frac <= 0.40
    top_mask = cum_pop_frac > 0.90

    bottom_mean = (
        np.average(values[bottom_mask], weights=weights[bottom_mask]) if bottom_mask.sum() > 0 else 0.0
    )
    top_mean = np.average(values[top_mask], weights=weights[top_mask]) if top_mask.sum() > 0 else 0.0

    return float(top_mean / bottom_mean) if bottom_mean > 0 else float("inf")


def compute_concentration_index(
    service: np.ndarray, rank: np.ndarray, population: np.ndarray
) -> float:
    """Wagstaff Concentration Index (CI) via the covariance method.

    Positive CI = service concentrated in areas with a higher rank value
    (e.g. less deprived, if rank is a deprivation rank). Negative CI = service
    concentrated in lower-rank (e.g. more deprived) areas.

    Args:
        service: Service level per areal unit.
        rank: Ranking variable per unit (e.g. deprivation rank; 1 = most
            deprived, higher = less deprived).
        population: Population weight per unit.

    Returns:
        Concentration Index in [-1, 1].
    """
    service = np.asarray(service, dtype=float)
    rank = np.asarray(rank, dtype=float)
    population = np.asarray(population, dtype=float)

    total_pop = population.sum()
    order = np.argsort(rank)
    pop_sorted = population[order]
    frac_rank = (np.cumsum(pop_sorted) - 0.5 * pop_sorted) / total_pop

    service_sorted = service[order]

    mean_service = np.average(service_sorted, weights=pop_sorted)
    cov = np.average((service_sorted - mean_service) * (frac_rank - 0.5), weights=pop_sorted)
    return float(2 * cov / mean_service) if mean_service > 0 else 0.0
