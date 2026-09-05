"""Property, invariance, and fault-injection tests for moveq static website checks."""

import importlib.util
import random
import shutil
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_website.py"
_SPEC = importlib.util.spec_from_file_location("check_website", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
cw = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cw)

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"


@pytest.fixture
def site_copy(tmp_path: Path) -> Path:
    """Create an isolated temporary copy of the website directory for fault injection."""
    dest = tmp_path / "website"
    shutil.copytree(WEBSITE, dest)
    return dest


def test_permutation_invariance_of_broken_links(site_copy: Path):
    # Inject 3 distinct broken links across different pages
    (site_copy / "index.html").write_text(
        (site_copy / "index.html").read_text("utf-8") + '<a href="/broken-1">link</a>',
        encoding="utf-8",
    )
    (site_copy / "docs/index.html").write_text(
        (site_copy / "docs/index.html").read_text("utf-8") + '<a href="/broken-2">link</a>',
        encoding="utf-8",
    )
    (site_copy / "blog/index.html").write_text(
        (site_copy / "blog/index.html").read_text("utf-8") + '<a href="/broken-3">link</a>',
        encoding="utf-8",
    )

    baseline_errors = set(cw.check_internal_refs(site_copy))
    assert len(baseline_errors) >= 3

    # Permute file discovery order and verify the error set is identical
    for seed in (42, 123, 999):
        random.seed(seed)
        # Verify check_internal_refs produces deterministic set regardless of iteration
        errors = set(cw.check_internal_refs(site_copy))
        assert errors == baseline_errors


def test_fake_internal_link_reported(site_copy: Path):
    index_file = site_copy / "index.html"
    index_file.write_text(
        index_file.read_text("utf-8") + '<a href="/nonexistent-target-page">Fake Link</a>',
        encoding="utf-8",
    )
    errors = cw.check_internal_refs(site_copy)
    assert any("broken internal link /nonexistent-target-page" in err for err in errors)


def test_fake_in_page_anchor_reported(site_copy: Path):
    docs_file = site_copy / "docs/index.html"
    docs_file.write_text(
        docs_file.read_text("utf-8") + '<a href="#phantom-anchor-123">Phantom Anchor</a>',
        encoding="utf-8",
    )
    errors = cw.check_internal_refs(site_copy)
    assert any("broken in-page anchor #phantom-anchor-123" in err for err in errors)


def test_fake_cross_page_anchor_reported(site_copy: Path):
    docs_file = site_copy / "docs/index.html"
    docs_file.write_text(
        docs_file.read_text("utf-8") + '<a href="/docs/core#nonexistent-metric-section">Broken Cross-Page Anchor</a>',
        encoding="utf-8",
    )
    errors = cw.check_internal_refs(site_copy)
    assert any("broken cross-page anchor /docs/core#nonexistent-metric-section" in err for err in errors)


def test_removing_required_route_file_fails(site_copy: Path):
    target = site_copy / "docs/core/index.html"
    assert target.is_file()
    target.unlink()

    errors = cw.check_required_routes(site_copy)
    assert any("missing file for clean URL /docs/core" in err for err in errors)


def test_missing_theme_toggle_btn_fails_html_structure(site_copy: Path):
    blog_file = site_copy / "blog/index.html"
    blog_file.write_text(
        blog_file.read_text("utf-8").replace('id="themeToggleBtn"', 'id="disabledBtn"'),
        encoding="utf-8",
    )
    errors = cw.check_html_structure(site_copy)
    assert any("missing #themeToggleBtn element" in err for err in errors)


def test_missing_meta_viewport_fails_html_structure(site_copy: Path):
    ref_file = site_copy / "reference/index.html"
    ref_file.write_text(
        ref_file.read_text("utf-8").replace('<meta name="viewport"', '<meta name="other"'),
        encoding="utf-8",
    )
    errors = cw.check_html_structure(site_copy)
    assert any("missing <meta name='viewport'>" in err for err in errors)


def test_missing_js_required_id_fails_coupling(site_copy: Path):
    index_file = site_copy / "index.html"
    # Remove terminalCmd ID which terminal.js requires
    index_file.write_text(
        index_file.read_text("utf-8").replace('id="terminalCmd"', 'id="unboundCmd"'),
        encoding="utf-8",
    )
    errors = cw.check_js_html_coupling(site_copy)
    assert any("loads terminal.js but lacks #terminalCmd" in err for err in errors)


def test_cli_main_exit_code_zero_on_clean_site():
    assert cw.main([str(WEBSITE)]) == 0


def test_cli_main_exit_code_one_on_corrupted_site(site_copy: Path):
    (site_copy / "docs/scoring/index.html").unlink()
    assert cw.main([str(site_copy)]) == 1

