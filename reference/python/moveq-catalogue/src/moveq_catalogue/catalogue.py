"""Same / replace / omit registry for cross-country section catalogues.

A base country defines a questionnaire (a list of section ids). Every other
country must explicitly decide, per section, whether to keep the same
question against local data (``same``), swap in a locally-meaningful
question (``replace``), or drop the section because no free small-area
variable exists yet (``omit``). ``Catalogue.validate()`` fails loudly on any
section left undecided, so a new country can never silently inherit an
unconsidered section from the base.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class SectionAction(str, Enum):
    SAME = "same"
    REPLACE = "replace"
    OMIT = "omit"


@dataclass(frozen=True)
class SectionMapping:
    section_id: str
    action: SectionAction
    country: str
    note: str | None = None
    replacement_title: str | None = None

    def __post_init__(self) -> None:
        if self.action is SectionAction.REPLACE and not self.replacement_title:
            raise ValueError(
                f"section '{self.section_id}': action=replace requires a replacement_title"
            )
        if self.action is SectionAction.OMIT and not self.note:
            raise ValueError(
                f"section '{self.section_id}': action=omit requires a note explaining why"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_id": self.section_id,
            "action": self.action.value,
            "country": self.country,
            "note": self.note,
            "replacement_title": self.replacement_title,
        }


class Catalogue:
    """A country's section-by-section decisions against a base questionnaire."""

    def __init__(self, base_sections: list[str], country: str):
        if len(base_sections) != len(set(base_sections)):
            raise ValueError("base_sections must not contain duplicates")
        self.base_sections = list(base_sections)
        self.country = country
        self._mappings: dict[str, SectionMapping] = {}

    def register(
        self,
        section_id: str,
        action: SectionAction,
        *,
        note: str | None = None,
        replacement_title: str | None = None,
    ) -> "Catalogue":
        if section_id not in self.base_sections:
            raise ValueError(
                f"'{section_id}' is not in the base questionnaire for {self.country}"
            )
        self._mappings[section_id] = SectionMapping(
            section_id=section_id,
            action=action,
            country=self.country,
            note=note,
            replacement_title=replacement_title,
        )
        return self

    def unregistered(self) -> list[str]:
        """Base sections this country has not yet decided on."""
        return [s for s in self.base_sections if s not in self._mappings]

    def validate(self) -> list[str]:
        """Return validation issues; an empty list means fully specified."""
        issues = []
        missing = self.unregistered()
        if missing:
            issues.append(
                f"{self.country}: {len(missing)} section(s) not mapped: {', '.join(missing)}"
            )
        return issues

    def summary(self) -> dict[str, int]:
        counts = {action.value: 0 for action in SectionAction}
        for mapping in self._mappings.values():
            counts[mapping.action.value] += 1
        return counts

    def mapping_for(self, section_id: str) -> SectionMapping | None:
        return self._mappings.get(section_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "country": self.country,
            "base_sections": list(self.base_sections),
            "mappings": [m.to_dict() for m in self._mappings.values()],
            "unregistered": self.unregistered(),
            "summary": self.summary(),
        }
