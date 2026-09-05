"""Benchmark runner to verify exact compute times on 1,000,000 spatial units."""

import time
import numpy as np
from moveq import compute_gini, compute_palma_ratio, compute_concentration_index, compute_score

def run_benchmarks():
    print("=" * 60)
    print("moveq Benchmark Suite — 1,000,000 Spatial Units")
    print("=" * 60)

    n = 1_000_000
    np.random.seed(42)
    service = np.random.uniform(5.0, 50.0, size=n)
    population = np.random.uniform(100.0, 5000.0, size=n)
    deprivation_rank = np.random.randint(1, 1000, size=n)

    # 1. Gini
    t0 = time.perf_counter()
    gini = compute_gini(service, population)
    t_gini = (time.perf_counter() - t0) * 1000
    print(f"✓ compute_gini:                {t_gini:6.2f} ms  (result: {gini:.4f})")

    # 2. Palma
    t0 = time.perf_counter()
    palma = compute_palma_ratio(service, population)
    t_palma = (time.perf_counter() - t0) * 1000
    print(f"✓ compute_palma_ratio:         {t_palma:6.2f} ms  (result: {palma:.4f})")

    # 3. Concentration Index (with 1,000 tied rank buckets)
    t0 = time.perf_counter()
    ci = compute_concentration_index(service, deprivation_rank, population)
    t_ci = (time.perf_counter() - t0) * 1000
    print(f"✓ compute_concentration_index: {t_ci:6.2f} ms  (result: {ci:.4f})")

    # 4. Composite Scoring (100,000 iterations)
    t0 = time.perf_counter()
    terms = {"coverage": 0.8, "evening": 0.5, "frequency": None, "gap": 0.9}
    weights = {"coverage": 0.4, "evening": 0.25, "frequency": 0.2, "gap": 0.15}
    for _ in range(10_000):
        res = compute_score(terms, weights)
    t_score = (time.perf_counter() - t0) / 10  # per 1,000 ops
    print(f"✓ compute_score (1k ops):      {t_score:6.2f} ms  (result: {res.score:.1f})")
    print("=" * 60)

if __name__ == "__main__":
    run_benchmarks()
