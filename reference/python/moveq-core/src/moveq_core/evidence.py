"""Claim ladder and in-memory case-manifest validation.

The six badges are the vocabulary for every published case. A descriptor is a
Frictionless Data Package JSON object with a ``moveq`` contract block. This
module does not read the filesystem: the caller supplies the descriptor dict
and, when files exist, a mapping of relative path to bytes. The CLI hashes
and loads those bytes.

Promotion is not a silent re-badge. ``claim_history`` must record the
condition that changed, and the destination badge's requirements must hold.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import dataclass
from typing import Any, Literal, Mapping

import numpy as np

from moveq_core.equity import (
    concentration_index_result,
    gini_result,
    palma_result,
)
from moveq_core.score import compute_score

ClaimBadge = Literal[
    "reproduced",
    "recomputed",
    "extended",
    "blocked",
    "demonstrated",
    "proposed",
]

CLAIM_BADGES: tuple[ClaimBadge, ...] = (
    "reproduced",
    "recomputed",
    "extended",
    "blocked",
    "demonstrated",
    "proposed",
)

PROMOTION_RULES: dict[ClaimBadge, str] = {
    "reproduced": (
        "Published per-unit values, a stated formula, obtainable data, a "
        "hashed resource, and a computed value within expected.tolerance. "
        "A case does not become REPRODUCED because a later run happened to agree."
    ),
    "recomputed": (
        "Source data available; moveq applies an independently implemented "
        "equivalent method. Never a match to a published figure that used a "
        "different, undisclosed, or incomplete formula."
    ),
    "extended": (
        "moveq adds a weighted, gradient-based, temporal or scenario analysis "
        "not reported originally. Requires obtainable unit-level inputs."
    ),
    "blocked": (
        "The published claim cannot be independently verified (missing "
        "per-unit data, formula, or transformations). blocked_reasons is "
        "required. expected is forbidden — do not compute a substitute and "
        "call it the published number."
    ),
    "demonstrated": (
        "Synthetic or illustrative scenario showing how a method behaves. "
        "expected is required so the constructed number cannot rot."
    ),
    "proposed": (
        "A compelling case whose data pipeline is not yet complete "
        "(licence, retrieval, or extract outstanding)."
    ),
}

_METRICS = ("gini", "palma", "ci", "score")
_OUTCOME_KINDS = ("benefit", "burden")
_WEIGHT_KINDS = ("population", "area", "need", "user", "unweighted")
_MISSING_POLICIES = ("reweight", "as_zero", "exclude", "bounds")
_VARIANTS = ("standard", "generalized", "erreygers", "wagstaff_normalized")
_RANK_DIRECTIONS = ("higher_is_advantaged", "higher_is_disadvantaged")
_METHOD_IDS = {
    "gini": "lorenz-trapezoid",
    "palma": "palma-split-40-90",
    "ci": "wagstaff-covariance",
}


@dataclass(frozen=True)
class ValidationIssue:
    check: Literal["schema", "hash", "method", "tolerance"]
    message: str


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    issues: tuple[ValidationIssue, ...]
    computed: float | None = None
    result: Any = None


def sha256_bytes(data: bytes) -> str:
    """Frictionless-style hash: ``sha256:<hex>``."""
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _issue(
    check: Literal["schema", "hash", "method", "tolerance"],
    message: str,
) -> ValidationIssue:
    return ValidationIssue(check=check, message=message)


def _is_mapping(value: object) -> bool:
    return isinstance(value, dict)


def _nonempty_str(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(_nonempty_str(item) for item in value)


def _moveq_block(descriptor: Mapping[str, Any]) -> dict[str, Any] | None:
    block = descriptor.get("moveq")
    return block if _is_mapping(block) else None


def _schema_issues(descriptor: Mapping[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not _nonempty_str(descriptor.get("name")):
        issues.append(_issue("schema", "descriptor.name is required"))
    if not _nonempty_str(descriptor.get("title")):
        issues.append(_issue("schema", "descriptor.title is required"))
    resources = descriptor.get("resources")
    if not isinstance(resources, list):
        issues.append(_issue("schema", "descriptor.resources must be a list"))
        resources = []

    moveq = _moveq_block(descriptor)
    if moveq is None:
        issues.append(_issue("schema", "descriptor.moveq is required"))
        return issues

    claim = moveq.get("claim")
    if claim not in CLAIM_BADGES:
        issues.append(
            _issue(
                "schema",
                "moveq.claim must be one of " + ", ".join(CLAIM_BADGES),
            )
        )

    if not _string_list(moveq.get("limitations")):
        issues.append(_issue("schema", "moveq.limitations is required and must be a non-empty list of strings"))

    if not _nonempty_str(moveq.get("original")):
        issues.append(_issue("schema", "moveq.original is required"))
    if not _nonempty_str(moveq.get("moveq_question")):
        issues.append(_issue("schema", "moveq.moveq_question is required"))

    outcome = moveq.get("outcome")
    if not _is_mapping(outcome):
        issues.append(_issue("schema", "moveq.outcome is required"))
        outcome = {}
    elif outcome.get("kind") not in _OUTCOME_KINDS:
        issues.append(_issue("schema", "moveq.outcome.kind must be 'benefit' or 'burden'"))
    if "kind" not in outcome:
        issues.append(_issue("schema", "contract decision outcome_kind is missing"))

    rank = moveq.get("rank")
    if not _is_mapping(rank):
        issues.append(_issue("schema", "moveq.rank is required (direction may be null)"))
        rank = {}
    direction = rank.get("direction")
    if direction is not None and direction not in _RANK_DIRECTIONS:
        issues.append(
            _issue(
                "schema",
                "moveq.rank.direction must be null or one of " + ", ".join(_RANK_DIRECTIONS),
            )
        )
    if "direction" not in rank:
        issues.append(_issue("schema", "contract decision rank_direction is missing"))

    method = moveq.get("method")
    if not _is_mapping(method):
        issues.append(_issue("schema", "moveq.method is required"))
        method = {}
    for key in ("weight_kind", "missing_policy", "variant"):
        if key not in method:
            issues.append(_issue("schema", f"contract decision {key} is missing"))

    weight_kind = method.get("weight_kind")
    if weight_kind is not None and weight_kind not in _WEIGHT_KINDS:
        issues.append(_issue("schema", "moveq.method.weight_kind is not a recognised kind"))
    missing_policy = method.get("missing_policy")
    if missing_policy is not None and missing_policy not in _MISSING_POLICIES:
        issues.append(_issue("schema", "moveq.method.missing_policy is not a recognised policy"))
    variant = method.get("variant")
    if variant is not None and variant not in _VARIANTS:
        issues.append(_issue("schema", "moveq.method.variant is not a recognised variant"))

    metric = method.get("metric")
    if metric is not None and metric not in _METRICS:
        issues.append(_issue("schema", "moveq.method.metric must be gini, palma, ci, score, or null"))

    expected = moveq.get("expected")
    if expected is None:
        if "expected" in moveq:
            issues.append(_issue("schema", "contract decision tolerance is missing"))
    elif not _is_mapping(expected):
        issues.append(_issue("schema", "moveq.expected must be an object"))
    else:
        if "tolerance" not in expected:
            issues.append(_issue("schema", "contract decision tolerance is missing"))
        elif expected.get("tolerance") is not None:
            try:
                if float(expected["tolerance"]) < 0:
                    issues.append(_issue("schema", "moveq.expected.tolerance must be non-negative"))
            except (TypeError, ValueError):
                issues.append(_issue("schema", "moveq.expected.tolerance must be numeric"))
        if "value" in expected and expected["value"] is not None:
            try:
                float(expected["value"])
            except (TypeError, ValueError):
                issues.append(_issue("schema", "moveq.expected.value must be numeric"))

    if claim == "blocked":
        if not _string_list(moveq.get("blocked_reasons")):
            issues.append(_issue("schema", "blocked cases require moveq.blocked_reasons"))
        if _is_mapping(expected) and expected.get("value") is not None:
            issues.append(
                _issue(
                    "schema",
                    "blocked cases must not carry expected.value — do not compute a substitute for the published figure",
                )
            )
        if metric is not None:
            issues.append(_issue("schema", "blocked cases must not declare a metric to run"))

    if claim == "demonstrated":
        if not (_is_mapping(expected) and expected.get("value") is not None):
            issues.append(_issue("schema", "demonstrated cases require expected.value so the constructed number cannot rot"))
        if metric is None:
            issues.append(_issue("schema", "demonstrated cases require moveq.method.metric"))

    if claim == "reproduced":
        sources = descriptor.get("sources")
        hashed = [
            item
            for item in resources
            if _is_mapping(item) and _nonempty_str(item.get("path")) and _nonempty_str(item.get("hash"))
        ]
        if not isinstance(sources, list) or not sources:
            issues.append(_issue("schema", "reproduced cases require descriptor.sources"))
        if not hashed:
            issues.append(_issue("schema", "reproduced cases require at least one hashed resource"))
        if not (_is_mapping(expected) and expected.get("value") is not None):
            issues.append(_issue("schema", "reproduced cases require expected.value"))
        if metric is None:
            issues.append(_issue("schema", "reproduced cases require moveq.method.metric"))

    history = moveq.get("claim_history")
    if history is not None:
        if not isinstance(history, list) or not history:
            issues.append(_issue("schema", "moveq.claim_history must be a non-empty list when present"))
        else:
            last = history[-1]
            if not _is_mapping(last):
                issues.append(_issue("schema", "claim_history entries must be objects"))
            else:
                if last.get("to") != claim:
                    issues.append(_issue("schema", "claim_history[-1].to must equal moveq.claim"))
                if last.get("from") not in CLAIM_BADGES:
                    issues.append(_issue("schema", "claim_history[-1].from must be a claim badge"))
                if not _nonempty_str(last.get("reason")):
                    issues.append(_issue("schema", "claim_history entries require a reason"))
                if not _nonempty_str(last.get("date")):
                    issues.append(_issue("schema", "claim_history entries require a date"))

    for index, resource in enumerate(resources):
        if not _is_mapping(resource):
            issues.append(_issue("schema", f"resources[{index}] must be an object"))
            continue
        if not _nonempty_str(resource.get("path")):
            issues.append(_issue("schema", f"resources[{index}].path is required"))
        resource_hash = resource.get("hash")
        if resource_hash is not None and not (
            isinstance(resource_hash, str) and resource_hash.startswith("sha256:")
        ):
            issues.append(
                _issue(
                    "schema",
                    f"resources[{index}].hash must use the sha256:<hex> form",
                )
            )

    return issues


def _hash_issues(
    descriptor: Mapping[str, Any],
    resource_bytes: Mapping[str, bytes],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    resources = descriptor.get("resources") or []
    if not isinstance(resources, list):
        return issues
    for resource in resources:
        if not _is_mapping(resource):
            continue
        path = resource.get("path")
        expected_hash = resource.get("hash")
        if not _nonempty_str(path) or not _nonempty_str(expected_hash):
            continue
        blob = resource_bytes.get(path)
        if blob is None:
            issues.append(_issue("hash", f"resource {path} is missing from supplied bytes"))
            continue
        actual = sha256_bytes(blob)
        if actual != expected_hash:
            issues.append(
                _issue(
                    "hash",
                    f"resource {path} hash mismatch: descriptor has {expected_hash}, bytes hash to {actual}",
                )
            )
    return issues


def _parse_csv(blob: bytes) -> list[dict[str, str]]:
    text = blob.decode("utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def _columns(rows: list[dict[str, str]], name: str) -> np.ndarray:
    try:
        return np.array([float(row[name]) for row in rows], dtype=float)
    except KeyError as exc:
        raise ValueError(f"CSV is missing column {name}") from exc
    except (TypeError, ValueError) as exc:
        raise ValueError(f"CSV column {name} is not numeric") from exc


def _first_tabular_rows(
    descriptor: Mapping[str, Any],
    resource_bytes: Mapping[str, bytes],
) -> list[dict[str, str]] | None:
    for resource in descriptor.get("resources") or []:
        if not _is_mapping(resource):
            continue
        path = resource.get("path")
        if not isinstance(path, str) or path not in resource_bytes:
            continue
        fmt = str(resource.get("format") or "").lower()
        if fmt == "csv" or path.endswith(".csv"):
            return _parse_csv(resource_bytes[path])
    return None


def _score_payload(
    descriptor: Mapping[str, Any],
    resource_bytes: Mapping[str, bytes],
) -> tuple[dict[str, Any], dict[str, float]]:
    for resource in descriptor.get("resources") or []:
        if not _is_mapping(resource):
            continue
        path = resource.get("path")
        if not isinstance(path, str) or path not in resource_bytes:
            continue
        fmt = str(resource.get("format") or "").lower()
        if fmt == "json" or path.endswith(".json"):
            payload = json.loads(resource_bytes[path].decode("utf-8"))
            if _is_mapping(payload) and "terms" in payload and "weights" in payload:
                return payload["terms"], payload["weights"]
    raise ValueError("score cases require a JSON resource with terms and weights")


def _run_method(
    descriptor: Mapping[str, Any],
    resource_bytes: Mapping[str, bytes],
) -> tuple[Any, list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    moveq = _moveq_block(descriptor) or {}
    method = moveq.get("method") if _is_mapping(moveq.get("method")) else {}
    metric = method.get("metric")
    source_id = descriptor.get("name") if isinstance(descriptor.get("name"), str) else None
    hashed = None
    for resource in descriptor.get("resources") or []:
        if _is_mapping(resource) and resource.get("hash"):
            hashed = resource.get("hash")
            break
    provenance = {
        "source_id": source_id,
        "data_hash": hashed if isinstance(hashed, str) else None,
    }

    try:
        if metric == "score":
            terms, weights = _score_payload(descriptor, resource_bytes)
            result = compute_score(
                terms=terms,
                weights=weights,
                missing_policy=method.get("missing_policy") or "reweight",
            )
            return result, issues
        rows = _first_tabular_rows(descriptor, resource_bytes)
        if rows is None:
            issues.append(_issue("method", f"metric {metric} requires a CSV resource"))
            return None, issues
        value_col = method.get("value_column")
        weight_col = method.get("weight_column")
        if not _nonempty_str(value_col) or not _nonempty_str(weight_col):
            issues.append(_issue("method", "gini, palma and ci require value_column and weight_column"))
            return None, issues
        values = _columns(rows, value_col)
        weights = _columns(rows, weight_col)
        if metric == "gini":
            return gini_result(values, weights, **provenance), issues
        if metric == "palma":
            return palma_result(values, weights, **provenance), issues
        if metric == "ci":
            rank_col = method.get("rank_column")
            direction = (moveq.get("rank") or {}).get("direction")
            if not _nonempty_str(rank_col) or direction not in _RANK_DIRECTIONS:
                issues.append(_issue("method", "ci requires rank_column and rank.direction"))
                return None, issues
            rank = _columns(rows, rank_col)
            return (
                concentration_index_result(
                    values,
                    rank,
                    weights,
                    rank_direction=direction,
                    outcome_kind=(moveq.get("outcome") or {}).get("kind"),
                    weight_kind=method.get("weight_kind"),
                    variant=method.get("variant"),
                    **provenance,
                ),
                issues,
            )
        issues.append(_issue("method", f"metric {metric} requires a CSV resource"))
        return None, issues
    except (ValueError, TypeError, json.JSONDecodeError, KeyError, UnicodeDecodeError) as exc:
        issues.append(_issue("method", f"declared method could not be run: {exc}"))
        return None, issues


def _result_value(result: Any) -> float | None:
    if result is None:
        return None
    if hasattr(result, "score"):
        return result.score
    return getattr(result, "value", None)


def _method_agreement(result: Any, metric: str | None) -> ValidationIssue | None:
    if result is None or metric in (None, "score"):
        return None
    expected_method = _METHOD_IDS.get(metric or "")
    actual = getattr(result, "method", None)
    if expected_method and actual != expected_method:
        return _issue(
            "method",
            f"declared metric {metric} ran as method {actual!r}, expected {expected_method!r}",
        )
    actual_metric = getattr(result, "metric", None)
    if actual_metric and actual_metric != metric:
        return _issue(
            "method",
            f"declared metric {metric} produced EquityResult.metric={actual_metric!r}",
        )
    return None


def validate_descriptor(
    descriptor: Mapping[str, Any],
    resource_bytes: Mapping[str, bytes] | None = None,
) -> ValidationReport:
    """Validate a Frictionless+moveq descriptor against in-memory resource bytes."""
    blobs = dict(resource_bytes or {})
    issues = _schema_issues(descriptor)
    if any(issue.check == "schema" for issue in issues):
        return ValidationReport(ok=False, issues=tuple(issues))

    issues.extend(_hash_issues(descriptor, blobs))

    moveq = _moveq_block(descriptor) or {}
    claim = moveq.get("claim")
    metric = (moveq.get("method") or {}).get("metric") if _is_mapping(moveq.get("method")) else None
    expected = moveq.get("expected") if _is_mapping(moveq.get("expected")) else None

    result = None
    computed: float | None = None
    if metric is not None:
        result, run_issues = _run_method(descriptor, blobs)
        issues.extend(run_issues)
        agreement = _method_agreement(result, metric)
        if agreement is not None:
            issues.append(agreement)
        computed = _result_value(result)

    if expected is not None and expected.get("value") is not None:
        if computed is None:
            issues.append(_issue("tolerance", "expected.value is set but no value was computed"))
        else:
            try:
                target = float(expected["value"])
                tol = float(expected.get("tolerance") or 0.0)
            except (TypeError, ValueError):
                target, tol = 0.0, 0.0
            if abs(float(computed) - target) > tol:
                issues.append(
                    _issue(
                        "tolerance",
                        f"computed {computed} is outside expected {target} ± {tol}",
                    )
                )

    return ValidationReport(
        ok=not issues,
        issues=tuple(issues),
        computed=computed,
        result=result,
    )


def validate_registry(registry: Mapping[str, Any]) -> ValidationReport:
    """A gallery registry is 30 entries, each with exactly one claim badge."""
    issues: list[ValidationIssue] = []
    cases = registry.get("cases")
    if not isinstance(cases, list):
        return ValidationReport(
            ok=False,
            issues=(_issue("schema", "registry.cases must be a list"),),
        )
    if len(cases) != 30:
        issues.append(_issue("schema", f"registry must contain 30 cases, found {len(cases)}"))
    seen: set[str] = set()
    for index, case in enumerate(cases):
        if not _is_mapping(case):
            issues.append(_issue("schema", f"cases[{index}] must be an object"))
            continue
        ident = case.get("id")
        if not _nonempty_str(ident):
            issues.append(_issue("schema", f"cases[{index}].id is required"))
        elif ident in seen:
            issues.append(_issue("schema", f"duplicate case id {ident}"))
        else:
            seen.add(ident)
        if case.get("claim") not in CLAIM_BADGES:
            issues.append(
                _issue(
                    "schema",
                    f"cases[{index}].claim must be exactly one of " + ", ".join(CLAIM_BADGES),
                )
            )
        if not _nonempty_str(case.get("spec")):
            issues.append(_issue("schema", f"cases[{index}].spec is required"))
        if not _nonempty_str(case.get("title")):
            issues.append(_issue("schema", f"cases[{index}].title is required"))
    return ValidationReport(ok=not issues, issues=tuple(issues))
