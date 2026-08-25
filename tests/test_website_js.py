"""JavaScript contract, invariant, and DOM coupling tests for moveq static site."""

import importlib.util
import re
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_website.py"
_SPEC = importlib.util.spec_from_file_location("check_website", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
cw = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cw)

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"
JS_DIR = WEBSITE / "assets" / "js"


def test_theme_js_contract():
    content = (JS_DIR / "theme.js").read_text(encoding="utf-8")
    assert "moveq-theme" in content, "theme.js must use 'moveq-theme' localStorage key"
    assert "data-theme" in content, "theme.js must manipulate 'data-theme' attribute"
    assert "window.toggleTheme" in content, "theme.js must define window.toggleTheme"
    assert "themeToggleBtn" in content, "theme.js must interact with #themeToggleBtn"
    assert "window.copyText" in content, "theme.js must define window.copyText"
    assert "window.switchInstaller" in content, "theme.js must define window.switchInstaller"


def test_version_js_contract():
    content = (JS_DIR / "version.js").read_text(encoding="utf-8")
    assert "SVamseekar/moveq" in content, "version.js must query the official SVamseekar/moveq repo"
    assert "moveq_github_latest_release" in content, "version.js must use the documented cache key"
    assert "5 * 60 * 1000" in content, "version.js must have 5-minute TTL"
    assert "repos/${REPO}/tags" in content or "repos/SVamseekar/moveq/tags" in content, "version.js must have tags fallback"
    assert "latestReleasePill" in content, "version.js must update #latestReleasePill"
    assert "releasePillText" in content, "version.js must update #releasePillText"
    assert "header-version-text" in content, "version.js must update version buttons"
    # Ensure offline / network failure degradation is handled via try/catch
    assert "catch" in content, "version.js must wrap network fetches in try/catch to degrade gracefully"


def test_search_js_docs_index_integrity():
    content = (JS_DIR / "search.js").read_text(encoding="utf-8")
    assert "searchModal" in content, "search.js must reference #searchModal"
    assert "searchInput" in content, "search.js must reference #searchInput"
    assert "searchResults" in content, "search.js must reference #searchResults"
    assert "window.openSearch" in content, "search.js must define window.openSearch"
    assert "window.closeSearch" in content, "search.js must define window.closeSearch"

    # Extract all paths from DOCS_INDEX in search.js
    paths = re.findall(r"""path:\s*["\']([^"\']+)["\']""", content)
    assert len(paths) >= 10, f"Expected at least 10 search index entries, found {len(paths)}"

    parsed_pages = cw.parse_all_pages(WEBSITE)
    for p in paths:
        parts = p.split("#")
        route = parts[0]
        fragment = parts[1] if len(parts) > 1 else None

        target_file = cw.resolve_clean_url(route, WEBSITE)
        assert target_file is not None, f"Search index path '{p}' route '{route}' failed to resolve"
        assert target_file.is_file(), f"Search target file {target_file} does not exist"

        if fragment:
            rel = target_file.relative_to(WEBSITE).as_posix()
            assert fragment in parsed_pages[rel].ids, (
                f"Search index target #{fragment} in '{p}' not found in {rel}"
            )


def test_playground_js_contract():
    content = (JS_DIR / "playground.js").read_text(encoding="utf-8")
    assert "lorenzCanvas" in content, "playground.js must reference #lorenzCanvas"
    assert "lowServiceSlider" in content or "sliderLowIncome" in content
    assert "highServiceSlider" in content or "sliderHighIncome" in content
    assert "calculateLorenzPoints" in content, "playground.js must calculate Lorenz curve points"


def test_terminal_js_contract():
    content = (JS_DIR / "terminal.js").read_text(encoding="utf-8")
    assert "TOUR_STATIONS" in content, "terminal.js must define TOUR_STATIONS"
    assert "terminalCmd" in content, "terminal.js must reference #terminalCmd"
    assert "terminalOutput" in content, "terminal.js must reference #terminalOutput"
    assert "selectStation" in content, "terminal.js must define station selection"


def test_benchmarks_js_contract():
    content = (JS_DIR / "benchmarks.js").read_text(encoding="utf-8")
    assert "BENCHMARK_DATA" in content, "benchmarks.js must define BENCHMARK_DATA"
    for key in ("gini", "palma", "ci", "score"):
        assert f"{key}:" in content or f'"{key}":' in content, f"Missing benchmark key {key}"
    assert "benchTitle" in content, "benchmarks.js must update #benchTitle"
    assert "benchSubtitle" in content, "benchmarks.js must update #benchSubtitle"
    assert "benchFootnote" in content, "benchmarks.js must update #benchFootnote"
    assert "benchBars" in content, "benchmarks.js must render into #benchBars"
    assert "switchBenchmark" in content, "benchmarks.js must define switchBenchmark"


def test_js_html_id_coupling():
    # Production check: all element IDs required by scripts must exist on the HTML pages that load them
    coupling_errors = cw.check_js_html_coupling(WEBSITE)
    assert coupling_errors == [], f"Found JS-HTML ID coupling errors: {coupling_errors}"

