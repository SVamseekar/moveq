"""Second implementations of the documented Gini, Palma, CI, and score formulas.

These exist so production tests can assert against an independent calculation,
not against `moveq_core` calling itself. Algorithms here are intentionally
different from `equity.py` / `score.py` (pairwise Gini, Python Palma split
loop, grouped-rank CI, dict score).
"""

from __future__ import annotations

import math

import numpy as np


def gini_pairwise(values: np.ndarray, weights: np.ndarray) -> float:
    """Relative mean difference: G = ΣΣ w_i w_j |y_i − y_j| / (2 W² μ)."""
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    total_weight = float(weights.sum())
    mean = float(np.average(values, weights=weights))
    if mean == 0.0:
        return 0.0
    diff = np.abs(values[:, None] - values[None, :])
    numerator = float(np.sum(weights[:, None] * weights[None, :] * diff))
    return numerator / (2.0 * total_weight * total_weight * mean)


def palma_split_loop(values: np.ndarray, weights: np.ndarray) -> float:
    """Palma via an explicit per-unit overlap loop (not vectorized clip)."""
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    order = np.argsort(values, kind="stable")
    values = values[order]
    weights = weights[order]
    total = float(weights.sum())
    bottom_cut = 0.40 * total
    top_cut = 0.90 * total
    cum = 0.0
    bottom_num = bottom_den = 0.0
    top_num = top_den = 0.0
    for y, w in zip(values.tolist(), weights.tolist()):
        start = cum
        end = cum + w
        bottom = max(0.0, min(end, bottom_cut) - start)
        top = max(0.0, end - max(start, top_cut))
        bottom_num += y * bottom
        bottom_den += bottom
        top_num += y * top
        top_den += top
        cum = end
    bottom_mean = bottom_num / bottom_den if bottom_den > 0 else 0.0
    top_mean = top_num / top_den if top_den > 0 else 0.0
    if bottom_mean == 0.0 and top_mean == 0.0:
        return 1.0
    if bottom_mean == 0.0:
        return float("inf")
    return top_mean / bottom_mean


def concentration_index_grouped(
    service: np.ndarray, rank: np.ndarray, population: np.ndarray
) -> float:
    """Wagstaff CI with an explicit tied-rank grouping loop (not bincount)."""
    service = np.asarray(service, dtype=float)
    rank = np.asarray(rank, dtype=float)
    population = np.asarray(population, dtype=float)
    live = population > 0
    service = service[live]
    rank = rank[live]
    population = population[live]
    order = np.argsort(rank, kind="stable")
    service = service[order]
    rank = rank[order]
    population = population[order]
    total = float(population.sum())
    n = service.size
    frac = np.empty(n, dtype=float)
    i = 0
    mass_before = 0.0
    while i < n:
        j = i + 1
        while j < n and rank[j] == rank[i]:
            j += 1
        group_mass = float(population[i:j].sum())
        frac[i:j] = (mass_before + 0.5 * group_mass) / total
        mass_before += group_mass
        i = j
    mean = float(np.average(service, weights=population))
    if mean == 0.0:
        return 0.0
    cov = float(np.average((service - mean) * (frac - 0.5), weights=population))
    return 2.0 * cov / mean


def _live_mean(service: np.ndarray, population: np.ndarray) -> float:
    live = population > 0
    return float(np.average(np.asarray(service, dtype=float)[live], weights=np.asarray(population, dtype=float)[live]))


def _in_unit_interval(service: np.ndarray, population: np.ndarray) -> bool:
    live = population > 0
    y = np.asarray(service, dtype=float)[live]
    return bool(np.all(y >= 0.0) and np.all(y <= 1.0))


def concentration_index_generalized(
    service: np.ndarray, rank: np.ndarray, population: np.ndarray
) -> float:
    """Generalised CI: μ · CI, using the grouped-rank relative index."""
    ci = concentration_index_grouped(service, rank, population)
    return _live_mean(service, population) * ci


def concentration_index_erreygers(
    service: np.ndarray, rank: np.ndarray, population: np.ndarray
) -> float | None:
    """Erreygers index: 4μ · CI when y is in [0, 1]; else undefined."""
    if not _in_unit_interval(service, population):
        return None
    ci = concentration_index_grouped(service, rank, population)
    return 4.0 * _live_mean(service, population) * ci


def concentration_index_wagstaff_normalized(
    service: np.ndarray, rank: np.ndarray, population: np.ndarray
) -> float | None:
    """Wagstaff normalised CI: CI / (1 − μ) on (0, 1) means in [0, 1]."""
    if not _in_unit_interval(service, population):
        return None
    mu = _live_mean(service, population)
    if mu == 0.0 or mu == 1.0:
        return None
    ci = concentration_index_grouped(service, rank, population)
    return ci / (1.0 - mu)


def composite_score(terms: dict[str, float | None], weights: dict[str, float]) -> float | None:
    """100 × Σ (w'_k · clip01(y_k)) with missing terms dropped and renormalised."""
    present: dict[str, float] = {}
    for key, design_w in weights.items():
        raw = terms.get(key)
        if raw is None:
            continue
        present[key] = max(0.0, min(1.0, float(raw)))
    if not present:
        return None
    weight_sum = sum(weights[k] for k in present)
    weighted = sum((weights[k] / weight_sum) * present[k] for k in present)
    return 100.0 * weighted


def composite_score_as_zero(terms: dict[str, float | None], weights: dict[str, float]) -> float:
    """100 × Σ (w_k / Σ w) · y_k with missing y_k treated as 0 (no reweight)."""
    total = sum(weights.values())
    acc = 0.0
    for key, design_w in weights.items():
        raw = terms.get(key)
        y = 0.0 if raw is None else max(0.0, min(1.0, float(raw)))
        acc += (design_w / total) * y
    return 100.0 * acc


def composite_score_bounds(
    terms: dict[str, float | None], weights: dict[str, float]
) -> tuple[float, float]:
    """Best- and worst-case scores filling missing terms with {0, 1}."""
    low_terms = {k: (0.0 if terms.get(k) is None else terms[k]) for k in weights}
    high_terms = {k: (1.0 if terms.get(k) is None else terms[k]) for k in weights}
    return composite_score_as_zero(low_terms, weights), composite_score_as_zero(high_terms, weights)


def finite_or_equal(a: float, b: float) -> bool:
    """True if both are inf with the same sign, or both are finite and close."""
    if math.isinf(a) or math.isinf(b):
        return math.isinf(a) and math.isinf(b) and (a > 0) == (b > 0)
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)
