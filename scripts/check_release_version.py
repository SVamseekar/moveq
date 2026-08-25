#!/usr/bin/env python3
"""Lockstep versions, __version__, and git release rules.

Usage:
    python scripts/check_release_version.py
        pyproject.toml and __init__.py must all match.

    python scripts/check_release_version.py v0.1.2
        also must match this tag (publish workflow).

    python scripts/check_release_version.py --git-rules
        also: package version must equal the latest v* tag, unless this is a
        release (CHANGELOG has ``## [X.Y.Z]`` and X.Y.Z is greater than the
        tag). Ordinary feature commits must not bump.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES: tuple[tuple[str, str], ...] = (
    ("moveq-core", "moveq_core"),
    ("moveq-catalogue", "moveq_catalogue"),
    ("moveq", "moveq"),
    ("moveq-cli", "moveq_cli"),
)
VERSION_RE = re.compile(r'^version\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
INIT_VERSION_RE = re.compile(r'^__version__\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def read_pyproject_version(pyproject: Path) -> str:
    text = pyproject.read_text(encoding="utf-8")
    match = VERSION_RE.search(text)
    if match is None:
        raise SystemExit(f"No version field in {pyproject}")
    return match.group(1)


def read_init_version(init_py: Path) -> str:
    text = init_py.read_text(encoding="utf-8")
    match = INIT_VERSION_RE.search(text)
    if match is None:
        raise SystemExit(f"No __version__ in {init_py}")
    return match.group(1)


def collect_versions(root: Path) -> dict[str, str]:
    versions: dict[str, str] = {}
    for dist_name, import_name in PACKAGES:
        pyproject = root / "reference" / "python" / dist_name / "pyproject.toml"
        init_py = root / "reference" / "python" / dist_name / "src" / import_name / "__init__.py"
        py_ver = read_pyproject_version(pyproject)
        init_ver = read_init_version(init_py)
        if py_ver != init_ver:
            raise SystemExit(
                f"{dist_name}: pyproject.toml has {py_ver!r} but "
                f"{import_name}/__init__.py has {init_ver!r}"
            )
        versions[dist_name] = py_ver
    return versions


def lockstep_version(versions: dict[str, str]) -> str:
    unique = set(versions.values())
    if len(unique) != 1:
        lines = ["Package versions are not lockstep:"]
        lines.extend(f"  {name}: {ver}" for name, ver in versions.items())
        raise SystemExit("\n".join(lines))
    return unique.pop()


def parse_semver(version: str) -> tuple[int, int, int] | None:
    match = SEMVER_RE.fullmatch(version)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def changelog_has_release_heading(changelog: str, version: str) -> bool:
    pattern = rf"^## \[{re.escape(version)}\](?:\s|$)"
    return re.search(pattern, changelog, re.MULTILINE) is not None


def evaluate_git_rules(package_version: str, latest_tag: str | None, changelog: str) -> str | None:
    """Return an error message, or None if the git rules pass."""
    if latest_tag is None:
        return "No v* git tags found. Fetch tags (git fetch --tags) and retry."
    if not latest_tag.startswith("v"):
        return f"Latest tag {latest_tag!r} is not a v* release tag."
    tag_version = latest_tag.removeprefix("v")
    if package_version == tag_version:
        return None
    parsed_pkg = parse_semver(package_version)
    parsed_tag = parse_semver(tag_version)
    if parsed_pkg is None:
        return f"Package version {package_version!r} is not X.Y.Z."
    if parsed_tag is None:
        return f"Tag version {tag_version!r} is not X.Y.Z."
    if not changelog_has_release_heading(changelog, package_version):
        return (
            f"Package version {package_version} does not match latest tag "
            f"{latest_tag}. Commits are not releases: do not bump version "
            "unless CHANGELOG.md has a '## [X.Y.Z]' heading for this release."
        )
    if parsed_pkg <= parsed_tag:
        return (
            f"Release version {package_version} must be greater than latest "
            f"tag {latest_tag}."
        )
    return None


def latest_v_tag(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "tag", "-l", "v*", "--sort=-version:refname"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or "git tag failed")
    tags = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return tags[0] if tags else None


def main(argv: list[str] | None = None, *, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tag",
        nargs="?",
        help="Release tag such as v0.1.2 (publish workflow)",
    )
    parser.add_argument(
        "--git-rules",
        action="store_true",
        help="Require version == latest v* tag unless this is a changelog release",
    )
    args = parser.parse_args(argv)

    if args.tag is not None and args.git_rules:
        print("Pass either a tag or --git-rules, not both.", file=sys.stderr)
        return 2

    try:
        actual = lockstep_version(collect_versions(root))
    except SystemExit as exc:
        if exc.code in (0, None):
            return 0
        if isinstance(exc.code, str):
            print(exc.code, file=sys.stderr)
            return 1
        print(exc, file=sys.stderr)
        return int(exc.code)

    if args.tag is not None:
        expected = args.tag.removeprefix("v")
        if actual != expected:
            print(
                f"Tag version {expected!r} does not match package version {actual!r}",
                file=sys.stderr,
            )
            return 1

    if args.git_rules:
        changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        error = evaluate_git_rules(actual, latest_v_tag(root), changelog)
        if error is not None:
            print(error, file=sys.stderr)
            return 1

    print(f"All packages at version {actual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
