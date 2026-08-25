"""Git release rules: ordinary commits must not bump; tags match packages."""

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_release_version.py"
_SPEC = importlib.util.spec_from_file_location("check_release_version", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
crv = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(crv)


def test_ordinary_commit_matching_tag_is_ok():
    assert crv.evaluate_git_rules("0.1.2", "v0.1.2", "## [Unreleased]\n") is None


def test_feature_commit_must_not_bump():
    err = crv.evaluate_git_rules("0.1.3", "v0.1.2", "## [Unreleased]\n")
    assert err is not None
    assert "Commits are not releases" in err
    assert "0.1.3" in err
    assert "v0.1.2" in err


def test_feature_commit_must_not_jump_to_minor():
    err = crv.evaluate_git_rules("0.2.0", "v0.1.2", "## [Unreleased]\n")
    assert err is not None
    assert "Commits are not releases" in err


def test_release_commit_is_ok_when_changelog_has_heading():
    changelog = "## [Unreleased]\n\n## [0.2.0] — 2026-08-25\n"
    assert crv.evaluate_git_rules("0.2.0", "v0.1.2", changelog) is None


def test_release_commit_requires_greater_version():
    changelog = "## [0.1.2] — 2026-08-25\n"
    err = crv.evaluate_git_rules("0.1.2", "v0.1.2", changelog)
    assert err is None  # equal to tag is ordinary, heading is irrelevant
    err = crv.evaluate_git_rules("0.1.1", "v0.1.2", "## [0.1.1] — 2026-01-01\n")
    assert err is not None
    assert "greater than latest tag" in err


def test_unreleased_heading_is_not_a_release():
    err = crv.evaluate_git_rules("0.2.0", "v0.1.2", "## [Unreleased]\n")
    assert err is not None


def test_missing_tags_fail_closed():
    err = crv.evaluate_git_rules("0.1.2", None, "## [Unreleased]\n")
    assert err is not None
    assert "git fetch --tags" in err


def test_changelog_heading_does_not_match_unreleased_substring():
    assert crv.changelog_has_release_heading("## [Unreleased]\n", "0.1.2") is False
    assert crv.changelog_has_release_heading("## [0.1.2] — 2026-08-25\n", "0.1.2") is True
    assert crv.changelog_has_release_heading("## [0.1.20] — 2026-08-25\n", "0.1.2") is False


def test_current_repo_satisfies_git_rules():
    assert crv.main(["--git-rules"]) == 0
