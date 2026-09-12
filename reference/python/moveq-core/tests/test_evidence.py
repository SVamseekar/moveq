"""Claim ladder, in-memory manifests, and validation (spec 04)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from oracles import composite_score

from moveq_core import evidence as evidence_mod
from moveq_core.evidence import (
    CLAIM_BADGES,
    PROMOTION_RULES,
    ValidationReport,
    sha256_bytes,
    validate_descriptor,
    validate_registry,
)


def _score_terms():
    return {"access": 0.8, "frequency": 0.6, "climate": None}


def _score_weights():
    return {"access": 0.50, "frequency": 0.25, "climate": 0.25}


def _terms_payload() -> bytes:
    return json.dumps(
        {"terms": _score_terms(), "weights": _score_weights()},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _demonstrated_score_descriptor(resource_bytes: bytes) -> dict:
    digest = sha256_bytes(resource_bytes)
    expected = composite_score(_score_terms(), _score_weights())
    return {
        "name": "t1.6-missing-term",
        "title": "Missing-term reweighting changes a composite ranking",
        "profile": "data-package",
        "licenses": [
            {
                "name": "BSD-3-Clause",
                "path": "https://spdx.org/licenses/BSD-3-Clause.html",
            }
        ],
        "sources": [
            {
                "title": "Constructed sensitivity example (spec 07 T1.6)",
                "path": "https://github.com/SVamseekar/moveq",
            }
        ],
        "resources": [
            {
                "name": "terms",
                "path": "terms.json",
                "format": "json",
                "hash": digest,
            }
        ],
        "moveq": {
            "claim": "demonstrated",
            "original": "A missing composite term can be dropped or zeroed.",
            "moveq_question": "Does the missing-term policy change the score enough to reorder a ranking?",
            "outcome": {
                "name": "composite_score",
                "unit": "score_0_100",
                "kind": "benefit",
                "nonnegative": True,
            },
            "rank": {"name": None, "direction": None},
            "population": {"column": None},
            "method": {
                "metric": "score",
                "variant": None,
                "weight_kind": "unweighted",
                "tie_policy": "weighted_midrank",
                "missing_policy": "reweight",
            },
            "expected": {"value": expected, "tolerance": 1e-9},
            "limitations": [
                "Constructed inputs; not a finding about a named NUTS2 region.",
                "The measure is descriptive, not causal.",
            ],
        },
    }


def test_claim_ladder_has_exactly_six_badges():
    assert CLAIM_BADGES == (
        "reproduced",
        "recomputed",
        "extended",
        "blocked",
        "demonstrated",
        "proposed",
    )


def test_each_badge_has_promotion_rule():
    assert set(PROMOTION_RULES) == set(CLAIM_BADGES)
    for badge, rule in PROMOTION_RULES.items():
        assert rule.strip(), badge


def test_valid_demonstrated_score_passes():
    payload = _terms_payload()
    report = validate_descriptor(
        _demonstrated_score_descriptor(payload),
        {"terms.json": payload},
    )
    assert report.ok
    assert report.issues == ()
    assert report.computed == pytest.approx(73.33333333333333)
    assert report.result is not None


def test_limitations_are_required():
    payload = _terms_payload()
    descriptor = _demonstrated_score_descriptor(payload)
    descriptor["moveq"]["limitations"] = []
    report = validate_descriptor(descriptor, {"terms.json": payload})
    assert not report.ok
    assert any(issue.check == "schema" for issue in report.issues)


def test_unknown_claim_fails_schema():
    payload = _terms_payload()
    descriptor = _demonstrated_score_descriptor(payload)
    descriptor["moveq"]["claim"] = "reproduce"
    report = validate_descriptor(descriptor, {"terms.json": payload})
    assert not report.ok
    assert any("claim" in issue.message for issue in report.issues)


def test_six_contract_decisions_must_be_present():
    payload = _terms_payload()
    descriptor = _demonstrated_score_descriptor(payload)
    del descriptor["moveq"]["method"]["missing_policy"]
    report = validate_descriptor(descriptor, {"terms.json": payload})
    assert not report.ok
    assert any("missing_policy" in issue.message for issue in report.issues)


def test_hash_mismatch_fails():
    payload = _terms_payload()
    descriptor = _demonstrated_score_descriptor(payload)
    descriptor["resources"][0]["hash"] = "sha256:" + "0" * 64
    report = validate_descriptor(descriptor, {"terms.json": payload})
    assert not report.ok
    assert any(issue.check == "hash" for issue in report.issues)


def test_missing_resource_bytes_fails_hash():
    payload = _terms_payload()
    descriptor = _demonstrated_score_descriptor(payload)
    report = validate_descriptor(descriptor, {})
    assert not report.ok
    assert any(issue.check == "hash" for issue in report.issues)


def test_wrong_expected_value_fails_tolerance():
    payload = _terms_payload()
    descriptor = _demonstrated_score_descriptor(payload)
    descriptor["moveq"]["expected"]["value"] = 55.0
    report = validate_descriptor(descriptor, {"terms.json": payload})
    assert not report.ok
    assert any(issue.check == "tolerance" for issue in report.issues)


def test_declared_method_must_match_what_ran():
    payload = _terms_payload()
    descriptor = _demonstrated_score_descriptor(payload)
    descriptor["moveq"]["method"]["metric"] = "gini"
    descriptor["moveq"]["method"]["value_column"] = "x"
    descriptor["moveq"]["method"]["weight_column"] = "w"
    report = validate_descriptor(descriptor, {"terms.json": payload})
    assert not report.ok
    assert any(issue.check in {"method", "schema"} for issue in report.issues)


def test_blocked_case_does_not_compute_a_value():
    descriptor = {
        "name": "t1.7-nursing-workforce",
        "title": "Published global nursing Gini cannot be checked from the paper",
        "profile": "data-package",
        "licenses": [
            {
                "name": "CC-BY-4.0",
                "path": "https://creativecommons.org/licenses/by/4.0/",
            }
        ],
        "sources": [
            {
                "title": "Kharazmi et al., BMC Nursing (2023)",
                "path": "https://doi.org/10.1186/s12912-023-01313-w",
            }
        ],
        "resources": [
            {
                "name": "table1",
                "path": "table1.json",
                "format": "json",
                "hash": sha256_bytes(b"{}"),
            }
        ],
        "moveq": {
            "claim": "blocked",
            "original": "Global nursing Gini is 0.667.",
            "moveq_question": "Can 0.667 be independently verified from the paper?",
            "outcome": {
                "name": "nurses_per_10000",
                "unit": "count_per_10000",
                "kind": "benefit",
                "nonnegative": True,
            },
            "rank": {"name": None, "direction": None},
            "population": {"column": None},
            "method": {
                "metric": None,
                "variant": None,
                "weight_kind": None,
                "tie_policy": None,
                "missing_policy": None,
            },
            "blocked_reasons": [
                "Stated formula is Gini = 1 − Σ(Xi × Yi), not the trapezoid Lorenz form.",
                "Table 1 publishes HDI-group aggregates only; there is no country table.",
                "Country-equal versus population weighting is undisclosed.",
            ],
            "limitations": [
                "The headline 0.667 cannot be checked from the article.",
                "This case documents the gap; it does not estimate a substitute Gini.",
            ],
        },
    }
    report = validate_descriptor(descriptor, {"table1.json": b"{}"})
    assert report.ok
    assert report.computed is None
    assert report.result is None


def test_blocked_case_must_not_carry_expected():
    payload = _terms_payload()
    descriptor = _demonstrated_score_descriptor(payload)
    descriptor["moveq"]["claim"] = "blocked"
    descriptor["moveq"]["blocked_reasons"] = ["no per-unit table"]
    report = validate_descriptor(descriptor, {"terms.json": payload})
    assert not report.ok
    assert any("expected" in issue.message for issue in report.issues)


def test_reproduced_requires_source_expected_and_hashed_data():
    descriptor = {
        "name": "too-thin",
        "title": "Thin",
        "profile": "data-package",
        "resources": [],
        "moveq": {
            "claim": "reproduced",
            "original": "Gini is 0.2",
            "moveq_question": "Does moveq match 0.2?",
            "outcome": {
                "name": "y",
                "unit": "1",
                "kind": "benefit",
                "nonnegative": True,
            },
            "rank": {"name": None, "direction": None},
            "population": {"column": None},
            "method": {
                "metric": "gini",
                "variant": None,
                "weight_kind": "population",
                "tie_policy": "weighted_midrank",
                "missing_policy": "exclude",
                "value_column": "y",
                "weight_column": "w",
            },
            "expected": {"value": 0.2, "tolerance": 1e-6},
            "limitations": ["none stated well"],
        },
    }
    report = validate_descriptor(descriptor, {})
    assert not report.ok
    messages = " ".join(issue.message for issue in report.issues)
    assert "reproduced" in messages.lower() or "source" in messages.lower() or "resource" in messages.lower()


def test_claim_history_to_must_match_current_claim():
    payload = _terms_payload()
    descriptor = _demonstrated_score_descriptor(payload)
    descriptor["moveq"]["claim_history"] = [
        {
            "from": "proposed",
            "to": "reproduced",
            "date": "2026-09-12",
            "reason": "history does not match the badge on the descriptor",
        }
    ]
    report = validate_descriptor(descriptor, {"terms.json": payload})
    assert not report.ok
    assert any("claim_history" in issue.message for issue in report.issues)


def test_registry_requires_thirty_unique_single_badge_entries():
    cases = []
    claims = (
        ["proposed"]
        + ["demonstrated"] * 2
        + ["extended"] * 10
        + ["blocked"]
        + ["demonstrated"] * 1
        + ["extended"] * 0
    )
    # Build a valid 30-row registry matching spec 07's counts.
    t1_claims = {
        "T1.1": "proposed",
        "T1.2": "demonstrated",
        "T1.3": "extended",
        "T1.4": "extended",
        "T1.5": "extended",
        "T1.6": "demonstrated",
        "T1.7": "blocked",
        "T1.8": "extended",
        "T1.9": "extended",
        "T1.10": "extended",
        "T1.11": "extended",
        "T1.12": "extended",
        "T1.13": "extended",
        "T1.14": "extended",
        "T1.15": "demonstrated",
    }
    for spec, claim in t1_claims.items():
        cases.append(
            {
                "id": spec.lower().replace(".", "-") + "-case",
                "spec": spec,
                "title": spec,
                "claim": claim,
            }
        )
    for i in range(1, 16):
        cases.append(
            {
                "id": f"t2.{i}-case",
                "spec": f"T2.{i}",
                "title": f"T2.{i}",
                "claim": "demonstrated",
            }
        )
    report = validate_registry({"cases": cases})
    assert report.ok
    assert len(cases) == 30


def test_registry_rejects_duplicate_ids_and_wrong_count():
    report = validate_registry(
        {
            "cases": [
                {"id": "a", "spec": "T1.1", "title": "A", "claim": "proposed"},
                {"id": "a", "spec": "T1.2", "title": "B", "claim": "demonstrated"},
            ]
        }
    )
    assert not report.ok


def test_registry_rejects_two_badges_or_unknown_badge():
    report = validate_registry(
        {
            "cases": [
                {
                    "id": "a",
                    "spec": "T1.1",
                    "title": "A",
                    "claim": "reproduced",
                    "also": "extended",
                }
            ]
        }
    )
    # unknown extra is fine; invalid claim values are not
    report = validate_registry(
        {
            "cases": [
                {"id": "a", "spec": "T1.1", "title": "A", "claim": "reproduce"}
            ]
        }
    )
    assert not report.ok


def test_sha256_bytes_uses_frictionless_algorithm_prefix():
    digest = sha256_bytes(b"abc")
    assert digest == "sha256:" + hashlib.sha256(b"abc").hexdigest()


def test_gini_csv_resource_runs_lorenz_method():
    csv_bytes = (
        "exposure,population\n1,100\n2,100\n3,100\n4,100\n5,100\n"
    ).encode("utf-8")
    descriptor = {
        "name": "tiny-gini",
        "title": "Tiny Gini",
        "profile": "data-package",
        "licenses": [{"name": "BSD-3-Clause", "path": "https://spdx.org/licenses/BSD-3-Clause.html"}],
        "sources": [{"title": "constructed", "path": "https://github.com/SVamseekar/moveq"}],
        "resources": [
            {
                "name": "rows",
                "path": "data.csv",
                "format": "csv",
                "hash": sha256_bytes(csv_bytes),
            }
        ],
        "moveq": {
            "claim": "demonstrated",
            "original": "A five-row Gini is well-defined.",
            "moveq_question": "Does the Lorenz-trapezoid Gini run on this CSV?",
            "outcome": {
                "name": "exposure",
                "unit": "1",
                "kind": "benefit",
                "nonnegative": True,
            },
            "rank": {"name": None, "direction": None},
            "population": {"column": "population"},
            "method": {
                "metric": "gini",
                "variant": None,
                "weight_kind": "population",
                "tie_policy": "weighted_midrank",
                "missing_policy": "exclude",
                "value_column": "exposure",
                "weight_column": "population",
            },
            "expected": {"value": 0.26666666666666666, "tolerance": 1e-9},
            "limitations": ["Constructed five-row vector."],
        },
    }
    # Expected from the pairwise oracle, not from compute_gini.
    from oracles import gini_pairwise
    import numpy as np

    expected = gini_pairwise(
        np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
        np.array([100.0, 100.0, 100.0, 100.0, 100.0]),
    )
    descriptor["moveq"]["expected"]["value"] = expected
    report = validate_descriptor(descriptor, {"data.csv": csv_bytes})
    assert report.ok
    assert report.result.method == "lorenz-trapezoid"
    assert report.result.source_id == "tiny-gini"


def test_committed_gallery_registry_matches_spec_07():
    root = Path(__file__).resolve().parents[4] / "examples" / "evidence"
    registry = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    report = validate_registry(registry)
    assert report.ok, report.issues
    cases = {row["id"]: row for row in registry["cases"]}
    assert cases["t1.1-greenspace"]["claim"] == "proposed"
    assert cases["t1.4-bus-travel-time"]["claim"] == "extended"
    assert cases["t1.6-missing-term"]["claim"] == "demonstrated"
    assert cases["t1.7-nursing-workforce"]["claim"] == "blocked"
    assert all(row["claim"] == "demonstrated" for row in registry["cases"] if row["spec"].startswith("T2."))
    assert not any(row["claim"] == "reproduced" for row in registry["cases"])
    published = [row for row in registry["cases"] if row.get("published")]
    for row in published:
        package = root / row["id"] / "datapackage.json"
        assert package.is_file(), row["id"]
        descriptor = json.loads(package.read_text(encoding="utf-8"))
        blobs = {
            item["path"]: (package.parent / item["path"]).read_bytes()
            for item in descriptor["resources"]
        }
        case_report = validate_descriptor(descriptor, blobs)
        assert case_report.ok, (row["id"], case_report.issues)
        assert descriptor["moveq"]["claim"] == row["claim"]


def _proposed_shell() -> dict:
    return {
        "name": "shell",
        "title": "Shell",
        "profile": "data-package",
        "resources": [],
        "moveq": {
            "claim": "proposed",
            "original": "x",
            "moveq_question": "y",
            "outcome": {"name": "y", "unit": "1", "kind": "benefit", "nonnegative": True},
            "rank": {"name": None, "direction": None},
            "population": {"column": None},
            "method": {
                "metric": None,
                "variant": None,
                "weight_kind": None,
                "tie_policy": None,
                "missing_policy": None,
            },
            "limitations": ["pipeline incomplete"],
        },
    }


def test_schema_rejects_incomplete_contract_objects():
    descriptor = _proposed_shell()
    descriptor["moveq"]["original"] = ""
    descriptor["moveq"]["moveq_question"] = "   "
    descriptor["moveq"]["outcome"] = "nope"
    descriptor["moveq"]["rank"] = None
    descriptor["moveq"]["method"] = None
    descriptor["moveq"]["expected"] = None
    report = validate_descriptor(descriptor, {})
    joined = " ".join(issue.message for issue in report.issues)
    assert "original" in joined
    assert "moveq_question" in joined
    assert "outcome" in joined
    assert "rank" in joined
    assert "method" in joined

    descriptor = _proposed_shell()
    descriptor["moveq"]["outcome"] = {"name": "y"}
    descriptor["moveq"]["rank"] = {"name": None}
    descriptor["moveq"]["expected"] = "0.1"
    report = validate_descriptor(descriptor, {})
    joined = " ".join(issue.message for issue in report.issues)
    assert "outcome_kind" in joined
    assert "rank_direction" in joined
    assert "expected must be an object" in joined

    descriptor = _proposed_shell()
    descriptor["moveq"]["expected"] = {"value": 1.0, "tolerance": "nope"}
    report = validate_descriptor(descriptor, {})
    assert any("tolerance must be numeric" in issue.message for issue in report.issues)

    descriptor = _proposed_shell()
    descriptor["moveq"]["expected"] = {"value": 1.0}
    report = validate_descriptor(descriptor, {})
    assert any("tolerance is missing" in issue.message for issue in report.issues)


def test_reproduced_requires_expected_and_metric_as_well_as_sources():
    descriptor = _proposed_shell()
    descriptor["moveq"]["claim"] = "reproduced"
    descriptor["sources"] = [{"title": "paper", "path": "https://example.com"}]
    descriptor["resources"] = [
        {"name": "rows", "path": "data.csv", "format": "csv", "hash": "sha256:" + "ab" * 32}
    ]
    report = validate_descriptor(descriptor, {})
    joined = " ".join(issue.message for issue in report.issues)
    assert "expected.value" in joined
    assert "metric" in joined


def test_non_numeric_csv_is_a_method_failure():
    csv_bytes = b"y,w\nx,1\n"
    descriptor = {
        "name": "bad-numeric",
        "title": "Bad numeric",
        "profile": "data-package",
        "licenses": [{"name": "BSD-3-Clause", "path": "https://spdx.org/licenses/BSD-3-Clause.html"}],
        "sources": [{"title": "constructed", "path": "https://github.com/SVamseekar/moveq"}],
        "resources": [
            {"name": "rows", "path": "data.csv", "format": "csv", "hash": sha256_bytes(csv_bytes)}
        ],
        "moveq": {
            "claim": "demonstrated",
            "original": "x",
            "moveq_question": "y",
            "outcome": {"name": "y", "unit": "1", "kind": "benefit", "nonnegative": True},
            "rank": {"name": None, "direction": None},
            "population": {"column": "w"},
            "method": {
                "metric": "gini",
                "variant": None,
                "weight_kind": "population",
                "tie_policy": "weighted_midrank",
                "missing_policy": "exclude",
                "value_column": "y",
                "weight_column": "w",
            },
            "expected": {"value": 0.0, "tolerance": 1e-9},
            "limitations": ["constructed"],
        },
    }
    report = validate_descriptor(descriptor, {"data.csv": csv_bytes})
    assert not report.ok
    assert any(issue.check == "method" for issue in report.issues)


def test_schema_rejects_missing_top_level_and_moveq():
    report = validate_descriptor({}, {})
    messages = " ".join(issue.message for issue in report.issues)
    assert "name" in messages
    assert "title" in messages
    assert "resources" in messages
    assert "moveq" in messages


def test_schema_rejects_invalid_enums_and_expected():
    descriptor = _proposed_shell()
    descriptor["moveq"]["outcome"]["kind"] = "fairness"
    descriptor["moveq"]["rank"]["direction"] = "sideways"
    descriptor["moveq"]["method"]["weight_kind"] = "people"
    descriptor["moveq"]["method"]["missing_policy"] = "drop"
    descriptor["moveq"]["method"]["variant"] = "wagstaff"
    descriptor["moveq"]["method"]["metric"] = "lorenz"
    descriptor["moveq"]["expected"] = {"value": "high", "tolerance": -1}
    descriptor["resources"] = [{"path": "x.csv", "hash": "md5:abc"}]
    report = validate_descriptor(descriptor, {})
    assert not report.ok
    joined = " ".join(issue.message for issue in report.issues)
    assert "outcome.kind" in joined
    assert "rank.direction" in joined
    assert "weight_kind" in joined
    assert "missing_policy" in joined
    assert "variant" in joined
    assert "metric" in joined
    assert "sha256" in joined


def test_schema_rejects_malformed_claim_history_and_resources():
    descriptor = _proposed_shell()
    descriptor["moveq"]["claim_history"] = []
    report = validate_descriptor(descriptor, {})
    assert not report.ok

    descriptor = _proposed_shell()
    descriptor["moveq"]["claim_history"] = ["not-an-object"]
    assert not validate_descriptor(descriptor, {}).ok

    descriptor = _proposed_shell()
    descriptor["moveq"]["claim_history"] = [{"from": "nope", "to": "proposed", "date": "", "reason": ""}]
    assert not validate_descriptor(descriptor, {}).ok

    descriptor = _proposed_shell()
    descriptor["resources"] = ["nope", {}]
    assert not validate_descriptor(descriptor, {}).ok


def test_blocked_requires_reasons():
    descriptor = _proposed_shell()
    descriptor["moveq"]["claim"] = "blocked"
    report = validate_descriptor(descriptor, {})
    assert not report.ok
    assert any("blocked_reasons" in issue.message for issue in report.issues)


def test_demonstrated_requires_metric_and_expected():
    descriptor = _proposed_shell()
    descriptor["moveq"]["claim"] = "demonstrated"
    report = validate_descriptor(descriptor, {})
    assert not report.ok
    joined = " ".join(issue.message for issue in report.issues)
    assert "expected.value" in joined
    assert "metric" in joined


def test_palma_and_ci_csv_resources_run():
    from oracles import concentration_index_grouped, palma_split_loop
    import numpy as np

    palma_csv = "y,w\n0,40\n0,20\n0,20\n10,10\n20,10\n".encode()
    y = np.array([0.0, 0.0, 0.0, 10.0, 20.0])
    w = np.array([40.0, 20.0, 20.0, 10.0, 10.0])
    palma_expected = palma_split_loop(y, w)
    palma_desc = {
        "name": "tiny-palma",
        "title": "Tiny Palma",
        "profile": "data-package",
        "licenses": [{"name": "BSD-3-Clause", "path": "https://spdx.org/licenses/BSD-3-Clause.html"}],
        "sources": [{"title": "constructed", "path": "https://github.com/SVamseekar/moveq"}],
        "resources": [
            {"name": "rows", "path": "data.csv", "format": "csv", "hash": sha256_bytes(palma_csv)}
        ],
        "moveq": {
            "claim": "demonstrated",
            "original": "Palma on a five-row vector.",
            "moveq_question": "Does palma-split-40-90 run?",
            "outcome": {"name": "y", "unit": "1", "kind": "benefit", "nonnegative": True},
            "rank": {"name": None, "direction": None},
            "population": {"column": "w"},
            "method": {
                "metric": "palma",
                "variant": None,
                "weight_kind": "population",
                "tie_policy": "weighted_midrank",
                "missing_policy": "exclude",
                "value_column": "y",
                "weight_column": "w",
            },
            "expected": {"value": palma_expected, "tolerance": 1e-9},
            "limitations": ["constructed"],
        },
    }
    palma_report = validate_descriptor(palma_desc, {"data.csv": palma_csv})
    assert palma_report.ok, palma_report.issues
    assert palma_report.result.method == "palma-split-40-90"

    ci_csv = "y,r,w\n10,1,100\n20,2,100\n30,3,100\n40,4,100\n".encode()
    service = np.array([10.0, 20.0, 30.0, 40.0])
    rank = np.array([1.0, 2.0, 3.0, 4.0])
    pop = np.array([100.0, 100.0, 100.0, 100.0])
    ci_expected = concentration_index_grouped(service, rank, pop)
    ci_desc = {
        "name": "tiny-ci",
        "title": "Tiny CI",
        "profile": "data-package",
        "licenses": [{"name": "BSD-3-Clause", "path": "https://spdx.org/licenses/BSD-3-Clause.html"}],
        "sources": [{"title": "constructed", "path": "https://github.com/SVamseekar/moveq"}],
        "resources": [
            {"name": "rows", "path": "data.csv", "format": "csv", "hash": sha256_bytes(ci_csv)}
        ],
        "moveq": {
            "claim": "demonstrated",
            "original": "CI on four equal-population rows.",
            "moveq_question": "Does wagstaff-covariance run?",
            "outcome": {"name": "y", "unit": "1", "kind": "benefit", "nonnegative": True},
            "rank": {"name": "r", "direction": "higher_is_advantaged"},
            "population": {"column": "w"},
            "method": {
                "metric": "ci",
                "variant": "standard",
                "weight_kind": "population",
                "tie_policy": "weighted_midrank",
                "missing_policy": "exclude",
                "value_column": "y",
                "weight_column": "w",
                "rank_column": "r",
            },
            "expected": {"value": ci_expected, "tolerance": 1e-9},
            "limitations": ["constructed"],
        },
    }
    ci_report = validate_descriptor(ci_desc, {"data.csv": ci_csv})
    assert ci_report.ok, ci_report.issues
    assert ci_report.result.method == "wagstaff-covariance"
    assert ci_report.result.source_id == "tiny-ci"


def test_method_fails_when_csv_or_columns_missing():
    descriptor = _demonstrated_score_descriptor(_terms_payload())
    descriptor["moveq"]["method"]["metric"] = "gini"
    descriptor["moveq"]["method"]["value_column"] = "y"
    descriptor["moveq"]["method"]["weight_column"] = "w"
    # JSON resource, not CSV.
    report = validate_descriptor(descriptor, {"terms.json": _terms_payload()})
    assert not report.ok
    assert any(issue.check == "method" for issue in report.issues)

    csv_bytes = b"a,b\n1,2\n"
    descriptor = {
        "name": "bad-cols",
        "title": "Bad cols",
        "profile": "data-package",
        "licenses": [{"name": "BSD-3-Clause", "path": "https://spdx.org/licenses/BSD-3-Clause.html"}],
        "sources": [{"title": "constructed", "path": "https://github.com/SVamseekar/moveq"}],
        "resources": [
            {"name": "rows", "path": "data.csv", "format": "csv", "hash": sha256_bytes(csv_bytes)}
        ],
        "moveq": {
            "claim": "demonstrated",
            "original": "x",
            "moveq_question": "y",
            "outcome": {"name": "y", "unit": "1", "kind": "benefit", "nonnegative": True},
            "rank": {"name": None, "direction": None},
            "population": {"column": None},
            "method": {
                "metric": "gini",
                "variant": None,
                "weight_kind": "population",
                "tie_policy": "weighted_midrank",
                "missing_policy": "exclude",
                "value_column": "y",
                "weight_column": "w",
            },
            "expected": {"value": 0.0, "tolerance": 1e-9},
            "limitations": ["constructed"],
        },
    }
    report = validate_descriptor(descriptor, {"data.csv": csv_bytes})
    assert not report.ok
    assert any(issue.check == "method" for issue in report.issues)


def test_score_fails_without_terms_payload():
    blob = b'{"no":"terms"}'
    descriptor = _demonstrated_score_descriptor(blob)
    descriptor["resources"][0]["hash"] = sha256_bytes(blob)
    report = validate_descriptor(descriptor, {"terms.json": blob})
    assert not report.ok
    assert any(issue.check == "method" for issue in report.issues)


def test_ci_requires_rank_fields():
    csv_bytes = b"y,w\n1,1\n2,1\n"
    descriptor = {
        "name": "ci-norank",
        "title": "CI without rank",
        "profile": "data-package",
        "licenses": [{"name": "BSD-3-Clause", "path": "https://spdx.org/licenses/BSD-3-Clause.html"}],
        "sources": [{"title": "constructed", "path": "https://github.com/SVamseekar/moveq"}],
        "resources": [
            {"name": "rows", "path": "data.csv", "format": "csv", "hash": sha256_bytes(csv_bytes)}
        ],
        "moveq": {
            "claim": "demonstrated",
            "original": "x",
            "moveq_question": "y",
            "outcome": {"name": "y", "unit": "1", "kind": "benefit", "nonnegative": True},
            "rank": {"name": None, "direction": None},
            "population": {"column": "w"},
            "method": {
                "metric": "ci",
                "variant": "standard",
                "weight_kind": "population",
                "tie_policy": "weighted_midrank",
                "missing_policy": "exclude",
                "value_column": "y",
                "weight_column": "w",
            },
            "expected": {"value": 0.0, "tolerance": 1e-9},
            "limitations": ["constructed"],
        },
    }
    report = validate_descriptor(descriptor, {"data.csv": csv_bytes})
    assert not report.ok
    assert any("rank" in issue.message for issue in report.issues)


def test_registry_rejects_non_list_and_incomplete_rows():
    assert not validate_registry({}).ok
    assert not validate_registry({"cases": ["nope"]}).ok
    assert not validate_registry({"cases": [{"id": "", "spec": "", "title": "", "claim": "proposed"}]}).ok


def test_expected_without_computed_value_fails_tolerance():
    descriptor = _proposed_shell()
    descriptor["moveq"]["expected"] = {"value": 0.5, "tolerance": 1e-6}
    report = validate_descriptor(descriptor, {})
    # proposed + expected but no metric → tolerance check
    assert not report.ok
    assert any(issue.check == "tolerance" for issue in report.issues)


def test_hash_and_loader_helpers_skip_malformed_resources():
    assert evidence_mod._hash_issues({"resources": "nope"}, {}) == []
    assert evidence_mod._hash_issues({"resources": ["x", {"path": "", "hash": ""}]}, {}) == []
    assert evidence_mod._first_tabular_rows({"resources": [None, {"path": 3}]}, {}) is None
    assert evidence_mod._first_tabular_rows({"resources": [{"path": "a.csv"}]}, {}) is None
    with pytest.raises(ValueError, match="terms and weights"):
        evidence_mod._score_payload({"resources": [None, {"path": 3}]}, {})


def test_gini_without_column_names_is_a_method_failure():
    csv_bytes = b"y,w\n1,1\n2,1\n"
    descriptor = {
        "name": "no-cols",
        "title": "No cols",
        "profile": "data-package",
        "licenses": [{"name": "BSD-3-Clause", "path": "https://spdx.org/licenses/BSD-3-Clause.html"}],
        "sources": [{"title": "constructed", "path": "https://github.com/SVamseekar/moveq"}],
        "resources": [
            {"name": "rows", "path": "data.csv", "format": "csv", "hash": sha256_bytes(csv_bytes)}
        ],
        "moveq": {
            "claim": "demonstrated",
            "original": "x",
            "moveq_question": "y",
            "outcome": {"name": "y", "unit": "1", "kind": "benefit", "nonnegative": True},
            "rank": {"name": None, "direction": None},
            "population": {"column": None},
            "method": {
                "metric": "gini",
                "variant": None,
                "weight_kind": "population",
                "tie_policy": "weighted_midrank",
                "missing_policy": "exclude",
            },
            "expected": {"value": 0.0, "tolerance": 1e-9},
            "limitations": ["constructed"],
        },
    }
    report = validate_descriptor(descriptor, {"data.csv": csv_bytes})
    assert not report.ok
    assert any("value_column" in issue.message for issue in report.issues)


def test_validation_report_is_frozen():
    payload = _terms_payload()
    report = validate_descriptor(
        _demonstrated_score_descriptor(payload),
        {"terms.json": payload},
    )
    assert isinstance(report, ValidationReport)
    with pytest.raises(AttributeError):
        report.ok = False  # type: ignore[misc]
