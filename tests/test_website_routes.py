"""Clean-URL resolution and routing tests for the moveq static website."""

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_website.py"
_SPEC = importlib.util.spec_from_file_location("check_website", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
cw = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cw)

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"

# Independent hardcoded expected mapping (do not call production code to generate)
INDEPENDENT_ROUTE_MAP: dict[str, str] = {
    "/": "index.html",
    "/docs": "docs/index.html",
    "/docs/core": "docs/core/index.html",
    "/docs/scoring": "docs/scoring/index.html",
    "/docs/catalogue": "docs/catalogue/index.html",
    "/docs/frames": "docs/frames/index.html",
    "/docs/cli": "docs/cli/index.html",
    "/guides": "guides/index.html",
    "/playground": "playground/index.html",
    "/reference": "reference/index.html",
    "/blog": "blog/index.html",
    "/assets/css/theme.css": "assets/css/theme.css",
    "/assets/js/version.js": "assets/js/version.js",
    "/assets/js/theme.js": "assets/js/theme.js",
    "/assets/js/benchmarks.js": "assets/js/benchmarks.js",
    "/assets/js/playground.js": "assets/js/playground.js",
    "/assets/js/search.js": "assets/js/search.js",
    "/assets/js/terminal.js": "assets/js/terminal.js",
    "/assets/images/favicon.svg": "assets/images/favicon.svg",
    "/assets/images/logo.svg": "assets/images/logo.svg",
}


@pytest.mark.parametrize("route,expected_rel_file", list(INDEPENDENT_ROUTE_MAP.items()))
def test_clean_url_resolves_to_expected_file(route: str, expected_rel_file: str):
    resolved = cw.resolve_clean_url(route, WEBSITE)
    assert resolved is not None, f"Route {route} failed to resolve"
    expected_path = WEBSITE / expected_rel_file
    assert resolved == expected_path
    assert resolved.is_file(), f"Target file for {route} does not exist on disk: {resolved}"


@pytest.mark.parametrize(
    "url_with_query_or_fragment,expected_rel_file",
    [
        ("/docs?x=1", "docs/index.html"),
        ("/docs#philosophy", "docs/index.html"),
        ("/docs?a=1&b=2#installation", "docs/index.html"),
        ("/docs/core?foo=bar#gini", "docs/core/index.html"),
        ("/guides?mode=dark#gtfs", "guides/index.html"),
        ("/assets/css/theme.css?v=0.1.2", "assets/css/theme.css"),
    ],
)
def test_query_and_fragment_stripping(url_with_query_or_fragment: str, expected_rel_file: str):
    resolved = cw.resolve_clean_url(url_with_query_or_fragment, WEBSITE)
    assert resolved == WEBSITE / expected_rel_file


@pytest.mark.parametrize(
    "invalid_url",
    [
        "/no-such-page",
        "/docs/nonexistent-subpage",
        "/assets/missing.png",
        "relative/path/without/leading/slash",
        "docs",
        "",
    ],
)
def test_invalid_urls_return_none(invalid_url: str):
    assert cw.resolve_clean_url(invalid_url, WEBSITE) is None


def test_sibling_html_branch(tmp_path: Path):
    # Tests the branch where /slug resolves to slug.html
    (tmp_path / "standalone.html").write_text("<h1>Standalone</h1>", encoding="utf-8")
    resolved = cw.resolve_clean_url("/standalone", tmp_path)
    assert resolved == tmp_path / "standalone.html"


def test_trailing_slash_behavior():
    # When trailingSlash is false in vercel.json, /docs/ resolves to docs/index.html
    resolved_with_slash = cw.resolve_clean_url("/docs/", WEBSITE)
    resolved_without_slash = cw.resolve_clean_url("/docs", WEBSITE)
    assert resolved_with_slash == WEBSITE / "docs/index.html"
    assert resolved_without_slash == WEBSITE / "docs/index.html"


def test_no_orphan_html_pages():
    # Every *.html file under website/ must be reachable by at least one clean URL in INDEPENDENT_ROUTE_MAP
    all_html_files = {p.resolve() for p in WEBSITE.rglob("*.html")}
    mapped_html_files = {
        (WEBSITE / rel).resolve()
        for route, rel in INDEPENDENT_ROUTE_MAP.items()
        if rel.endswith(".html")
    }
    orphan_files = all_html_files - mapped_html_files
    assert not orphan_files, f"Found orphan HTML files not mapped by any clean URL route: {orphan_files}"

