"""Demonstration only. Not a shipped comparison capability.

Comparability holds because the pair is constructed: the same four zones,
the same populations, the same units. A general diff of two real vintages
is rejected in the comparability note. This script does not add a CLI
command or a regression check.

    python examples/distributional_difference/run.py
"""

from __future__ import annotations

import numpy as np

from moveq import compare_results, gini_result

# Same zones, same population. Constructed so the mean can rise while the
# bottom 40% of population receives a smaller share of service.
WEIGHTS = np.array([25.0, 25.0, 25.0, 25.0])
BASELINE = np.array([10.0, 10.0, 10.0, 10.0])
PROPOSAL = np.array([5.0, 5.0, 20.0, 20.0])


def bottom_share(values: np.ndarray, weights: np.ndarray, cut: float = 0.40) -> float:
    order = np.argsort(values, kind="stable")
    values = values[order]
    weights = weights[order]
    total_w = float(weights.sum())
    total_service = float((values * weights).sum())
    cum = np.cumsum(weights)
    before = cum - weights
    overlap = np.clip(np.minimum(cum, cut * total_w) - before, 0, None)
    return float((values * overlap).sum() / total_service)


def demonstrate(seed: int = 4, n_boot: int = 200) -> dict[str, float | str]:
    base = gini_result(BASELINE, WEIGHTS, weight_kind="population")
    prop = gini_result(PROPOSAL, WEIGHTS, weight_kind="population")
    diff = compare_results(
        base,
        prop,
        uncertainty="bootstrap",
        n_boot=n_boot,
        seed=seed,
        baseline_inputs=(BASELINE, WEIGHTS),
        proposal_inputs=(PROPOSAL, WEIGHTS),
    )
    mean_base = float(np.average(BASELINE, weights=WEIGHTS))
    mean_prop = float(np.average(PROPOSAL, weights=WEIGHTS))
    share_base = bottom_share(BASELINE, WEIGHTS)
    share_prop = bottom_share(PROPOSAL, WEIGHTS)
    return {
        "label": "demonstration",
        "mean_baseline": mean_base,
        "mean_proposal": mean_prop,
        "bottom_share_baseline": share_base,
        "bottom_share_proposal": share_prop,
        "gini_baseline": float(base.value),
        "gini_proposal": float(prop.value),
        "difference": float(diff.difference),
        "ci_low": float(diff.ci_low),
        "ci_high": float(diff.ci_high),
    }


def main() -> None:
    row = demonstrate()
    print("DEMONSTRATION — not a shipped capability")
    print("Attestation: same zones, same population, constructed pair")
    print(f"Mean service     {row['mean_baseline']:.1f} -> {row['mean_proposal']:.1f}")
    print(
        "Bottom 40% share "
        f"{row['bottom_share_baseline']:.2f} -> {row['bottom_share_proposal']:.2f}"
    )
    print(f"Gini             {row['gini_baseline']:.3f} -> {row['gini_proposal']:.3f}")
    print(
        f"Gini difference  {row['difference']:.3f} "
        f"[{row['ci_low']:.3f}, {row['ci_high']:.3f}]"
    )
    print("The mean rose. The bottom share fell. That is a distribution, not a cause.")


if __name__ == "__main__":
    main()
