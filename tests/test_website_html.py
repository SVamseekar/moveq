"""Parsed HTML integrity, link resolution, and structural validation tests."""

import html.parser
import importlib.util
import urllib.parse
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_website.py"
_SPEC = importlib.util.spec_from_file_location("check_website", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
cw = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cw)

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"

HTML_FILES = sorted(list(WEBSITE.rglob("*.html")))


@pytest.fixture(scope="module")
def parsed_pages():
    return cw.parse_all_pages(WEBSITE)


def test_html_file_count():
    # Exactly 11 index.html files under website/
    assert len(HTML_FILES) == 11, f"Expected 11 HTML files, found {len(HTML_FILES)}"


@pytest.mark.parametrize("html_file", HTML_FILES, ids=lambda p: str(p.relative_to(WEBSITE)))
def test_html_document_structure(parsed_pages, html_file: Path):
    rel = html_file.relative_to(WEBSITE).as_posix()
    page = parsed_pages[rel]

    assert page.has_html, f"{rel}: missing <html> tag"
    assert page.html_attrs.get("lang") == "en", f"{rel}: <html> must have lang='en'"
    assert page.html_attrs.get("data-theme") is not None, f"{rel}: <html> must have data-theme"
    assert page.head_count == 1, f"{rel}: expected 1 <head>, got {page.head_count}"
    assert page.body_count == 1, f"{rel}: expected 1 <body>, got {page.body_count}"
    assert page.meta_viewport, f"{rel}: missing <meta name='viewport'>"
    assert page.has_favicon, f"{rel}: missing favicon link"
    assert page.has_theme_css, f"{rel}: missing theme.css link"
    assert page.has_theme_toggle_btn, f"{rel}: missing #themeToggleBtn"
    assert page.theme_toggle_has_accessible_name, f"{rel}: #themeToggleBtn missing accessible name"


@pytest.mark.parametrize("html_file", HTML_FILES, ids=lambda p: str(p.relative_to(WEBSITE)))
def test_no_empty_href_or_src(parsed_pages, html_file: Path):
    rel = html_file.relative_to(WEBSITE).as_posix()
    page = parsed_pages[rel]
    assert not page.empty_attributes, f"{rel} has empty href or src: {page.empty_attributes}"


@pytest.mark.parametrize("html_file", HTML_FILES, ids=lambda p: str(p.relative_to(WEBSITE)))
def test_navigation_completeness(parsed_pages, html_file: Path):
    rel = html_file.relative_to(WEBSITE).as_posix()
    page = parsed_pages[rel]
    required_nav = {"/docs", "/guides", "/reference", "/playground", "/blog"}
    missing = required_nav - page.nav_hrefs
    assert not missing, f"{rel}: Navigation bar missing links to {missing}"


@pytest.mark.parametrize("html_file", HTML_FILES, ids=lambda p: str(p.relative_to(WEBSITE)))
def test_in_page_anchors_exist(parsed_pages, html_file: Path):
    rel = html_file.relative_to(WEBSITE).as_posix()
    page = parsed_pages[rel]
    for href in page.hrefs:
        if href.startswith("#"):
            anchor = href[1:]
            assert anchor in page.ids, f"{rel}: in-page anchor '#{anchor}' has no matching element id"


@pytest.mark.parametrize("html_file", HTML_FILES, ids=lambda p: str(p.relative_to(WEBSITE)))
def test_root_relative_links_and_cross_page_anchors(parsed_pages, html_file: Path):
    rel = html_file.relative_to(WEBSITE).as_posix()
    page = parsed_pages[rel]
    for href in page.hrefs:
        if href.startswith("/"):
            parsed = urllib.parse.urlparse(href)
            target = cw.resolve_clean_url(parsed.path, WEBSITE)
            assert target is not None, f"{rel}: root-relative link '{href}' cannot be resolved"
            assert target.is_file(), f"{rel}: link '{href}' points to missing file {target}"

            if parsed.fragment:
                target_rel = target.relative_to(WEBSITE).as_posix()
                if target_rel in parsed_pages:
                    assert parsed.fragment in parsed_pages[target_rel].ids, (
                        f"{rel}: cross-page anchor '{href}' fragment '#{parsed.fragment}' "
                        f"not found in {target_rel}"
                    )


@pytest.mark.parametrize("html_file", HTML_FILES, ids=lambda p: str(p.relative_to(WEBSITE)))
def test_image_and_svg_accessibility(parsed_pages, html_file: Path):
    rel = html_file.relative_to(WEBSITE).as_posix()
    page = parsed_pages[rel]
    assert not page.imgs_missing_alt, f"{rel}: images missing alt: {page.imgs_missing_alt}"


def test_html_structure_check_helper():
    assert cw.check_html_structure(WEBSITE) == []
    assert cw.check_internal_refs(WEBSITE) == []

