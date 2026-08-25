"""Static website suite: clean URLs, no Node build, HTML integrity, and HTTP routing."""

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_website.py"
_SPEC = importlib.util.spec_from_file_location("check_website", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
cw = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cw)

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"


def test_vercel_json_is_static_other():
    assert cw.check_vercel_json(WEBSITE) == []


def test_package_json_has_no_node_build():
    assert cw.check_package_json(WEBSITE) == []


def test_required_routes_resolve_to_files():
    assert cw.check_required_routes(WEBSITE) == []


def test_internal_href_and_src_resolve():
    assert cw.check_internal_refs(WEBSITE) == []
    assert cw.internal_refs(WEBSITE)  # pages actually declare root-relative assets


def test_html_structure_and_accessibility():
    assert cw.check_html_structure(WEBSITE) == []


def test_js_html_id_coupling():
    assert cw.check_js_html_coupling(WEBSITE) == []


def test_dev_server_returns_200_for_required_routes():
    assert cw.check_http_routes(WEBSITE) == []


def test_root_and_asset_resolution():
    assert cw.resolve_clean_url("/", WEBSITE).name == "index.html"
    assert cw.resolve_clean_url("/docs/core", WEBSITE).as_posix().endswith("docs/core/index.html")
    assert cw.resolve_clean_url("/assets/css/theme.css", WEBSITE).name == "theme.css"
    assert cw.resolve_clean_url("/no-such-page", WEBSITE) is None


def test_full_website_check_passes():
    assert cw.collect_errors(WEBSITE) == []
