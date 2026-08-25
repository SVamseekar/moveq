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

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

_trapezoid = getattr(np, "trapezoid", getattr(np, "trapz", None))
if _trapezoid is None:
    raise ImportError("NumPy has neither 'trapezoid' nor 'trapz' — unsupported version")

MetricId = Literal["gini", "palma", "ci"]

_PALMA_BOTTOM_CUT = 0.40
_PALMA_TOP_CUT = 0.90


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


def _drop_unpopulated(
    *arrays: np.ndarray, population: np.ndarray
) -> tuple[tuple[np.ndarray, ...], int, int, float]:
    live = population > 0
    n_dropped = int(np.count_nonzero(~live))
    if n_dropped:
        arrays = tuple(a[live] for a in arrays)
        population = population[live]
    return arrays, int(population.size), n_dropped, float(population.sum())


@dataclass(frozen=True)
class EquityResult:
    """Auditable result of a population-weighted equity metric.

    ``value`` is the same number returned by the corresponding ``compute_*``
    function. ``method`` identifies the documented algorithm; parameters
    such as Palma's 40%/90% cuts live in ``parameters``, not a parallel
    versioning scheme.
    """

    metric: MetricId
    value: float
    method: str
    n_areas: int
    n_dropped: int
    total_population: float
    parameters: dict[str, Any]
    warnings: list[str]
    note: str | None
    context: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "value": self.value,
            "method": self.method,
            "n_areas": self.n_areas,
            "n_dropped": self.n_dropped,
            "total_population": self.total_population,
            "parameters": dict(self.parameters),
            "warnings": list(self.warnings),
            "note": self.note,
            "context": dict(self.context),
        }


def gini_result(
    values: np.ndarray, weights: np.ndarray, *, context: dict[str, str] | None = None
) -> EquityResult:
    """Population-weighted Gini coefficient with audit fields.

    See :func:`compute_gini` for the numeric definition.
    """
    values, weights = _prepare_weighted(values, weights)
    (values, weights), n_areas, n_dropped, total_population = _drop_unpopulated(
        values, weights, population=weights
    )

    warnings: list[str] = []
    note = None
    total_service = float((values * weights).sum())
    if total_service == 0:
        value = 0.0
        warnings.append("zero total service treated as Gini = 0")
        note = "Zero total service (nothing to distribute) is treated as perfect equality."
    else:
        order = np.argsort(values, kind="stable")
        values = values[order]
        weights = weights[order]
        cum_pop = np.cumsum(weights) / weights.sum()
        cum_service = np.cumsum(values * weights) / total_service
        cum_pop = np.concatenate([[0], cum_pop])
        cum_service = np.concatenate([[0], cum_service])
        lorenz_area = _trapezoid(cum_service, cum_pop)
        value = float(1 - 2 * lorenz_area)

    return EquityResult(
        metric="gini",
        value=value,
        method="lorenz-trapezoid",
        n_areas=n_areas,
        n_dropped=n_dropped,
        total_population=total_population,
        parameters={},
        warnings=warnings,
        note=note,
        context=dict(context or {}),
    )


def palma_result(
    values: np.ndarray, weights: np.ndarray, *, context: dict[str, str] | None = None
) -> EquityResult:
    """Palma ratio with audit fields.

    See :func:`compute_palma_ratio` for the numeric definition.
    """
    values, weights = _prepare_weighted(values, weights)
    (values, weights), n_areas, n_dropped, total_population = _drop_unpopulated(
        values, weights, population=weights
    )

    order = np.argsort(values, kind="stable")
    values = values[order]
    weights = weights[order]

    total = weights.sum()
    cum_weight = np.cumsum(weights)
    cum_before = cum_weight - weights

    bottom_cut = _PALMA_BOTTOM_CUT * total
    top_cut = _PALMA_TOP_CUT * total

    bottom_overlap = np.clip(np.minimum(cum_weight, bottom_cut) - cum_before, 0, None)
    top_overlap = np.clip(cum_weight - np.maximum(cum_before, top_cut), 0, None)

    bottom_weight = bottom_overlap.sum()
    top_weight = top_overlap.sum()

    bottom_mean = float(np.sum(values * bottom_overlap) / bottom_weight) if bottom_weight > 0 else 0.0
    top_mean = float(np.sum(values * top_overlap) / top_weight) if top_weight > 0 else 0.0

    warnings: list[str] = []
    note = None
    if bottom_mean == 0.0 and top_mean == 0.0:
        value = 1.0
        warnings.append("zero total service treated as Palma = 1")
        note = "All-zero service is treated as equality (Palma = 1)."
    elif bottom_mean > 0:
        value = float(top_mean / bottom_mean)
    else:
        value = float("inf")
        warnings.append("bottom 40% mean service is zero; Palma is infinite")
        note = "The bottom 40% has zero mean service while the top 10% does not."

    return EquityResult(
        metric="palma",
        value=value,
        method="palma-split-40-90",
        n_areas=n_areas,
        n_dropped=n_dropped,
        total_population=total_population,
        parameters={"bottom_cut": _PALMA_BOTTOM_CUT, "top_cut": _PALMA_TOP_CUT},
        warnings=warnings,
        note=note,
        context=dict(context or {}),
    )


def concentration_index_result(
    service: np.ndarray,
    rank: np.ndarray,
    population: np.ndarray,
    *,
    context: dict[str, str] | None = None,
) -> EquityResult:
    """Wagstaff Concentration Index with audit fields.

    See :func:`compute_concentration_index` for the numeric definition.
    """
    service, population = _prepare_weighted(
        service, population, values_name="service", weights_name="population", allow_negative_values=True
    )
    rank = _as_1d("rank", rank)
    if rank.shape != service.shape:
        raise ValueError("rank must have the same length as service")
    if not np.all(np.isfinite(rank)):
        raise ValueError("rank must be finite")

    (service, rank, population), n_areas, n_dropped, total_population = _drop_unpopulated(
        service, rank, population, population=population
    )

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
    frac_rank = (group_before + 0.5 * group_pop)[group_id] / total_population

    mean_service = float(np.average(service_sorted, weights=pop_sorted))
    warnings: list[str] = []
    note = None
    if mean_service == 0.0:
        value = 0.0
        warnings.append("zero mean service treated as Concentration Index = 0")
        note = "Zero mean service is treated as CI = 0."
    else:
        cov = float(
            np.average((service_sorted - mean_service) * (frac_rank - 0.5), weights=pop_sorted)
        )
        value = float(2 * cov / mean_service)

    return EquityResult(
        metric="ci",
        value=value,
        method="wagstaff-covariance",
        n_areas=n_areas,
        n_dropped=n_dropped,
        total_population=total_population,
        parameters={},
        warnings=warnings,
        note=note,
        context=dict(context or {}),
    )


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
    return gini_result(values, weights).value


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
    return palma_result(values, weights).value


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
    return concentration_index_result(service, rank, population).value
