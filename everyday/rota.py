"""Recurring-duty rota. Calls moveq-core. Keeps nothing.

The reply is an action in ordinary words. It does not return a coefficient.
"""

from __future__ import annotations

import numpy as np

from moveq_core.equity import compute_gini

ASSUMPTIONS = (
    "Each person counts once. Turns are treated as equal. If someone took more turns, this suggestion can change.",
    "Hours left blank are left out. They are not treated as zero. Filling them in can change who should take the next duty.",
    "Nothing you type is stored.",
)


def _times(ratio: float) -> str:
    if ratio >= 2.5:
        return "three times"
    if ratio >= 1.5:
        return "twice"
    return "more than"


def advise(people: list[dict]) -> dict[str, object]:
    """people: {"name": str, "hours": float | None}."""
    missing = [person["name"] for person in people if person.get("hours") is None]
    present = [person for person in people if person.get("hours") is not None]
    if len(present) < 2:
        action = "Add at least two people and their hours before there is a suggestion."
    else:
        hours = np.array([float(person["hours"]) for person in present], dtype=float)
        weights = np.ones(len(present))
        gini = compute_gini(hours, weights)
        if gini == 0:
            action = "The hours match. Keep sharing the duties as you are."
        else:
            index = int(np.argmax(hours))
            share = float(hours.mean())
            name = present[index]["name"]
            action = (
                f"{name} did about {_times(float(hours[index]) / share)} their share of the hours. "
                "Give the next long duty to someone else."
            )
    if missing:
        names = ", ".join(missing)
        action += f" {names} had no hours, so they are not in this suggestion."
    return {"action": action, "assumptions": list(ASSUMPTIONS)}
