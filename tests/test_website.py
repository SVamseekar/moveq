"""Static website: clean URLs, no Node build, internal links resolve."""

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_website.py"
_SPEC = importlib.util.spec_from_file_location("check_website", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
cw = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cw)


def test_vercel_json_is_static_other():
    assert cw.check_vercel_json() == []


def test_package_json_has_no_node_build():
    assert cw.check_package_json() == []


def test_required_routes_resolve_to_files():
    assert cw.check_required_routes() == []


def test_internal_href_and_src_resolve():
    assert cw.check_internal_refs() == []
    assert cw.internal_refs()  # pages actually declare root-relative assets


def test_dev_server_returns_200_for_required_routes():
    assert cw.check_http_routes() == []


def test_root_and_asset_resolution():
    assert cw.resolve_clean_url("/").name == "index.html"
    assert cw.resolve_clean_url("/docs/core").as_posix().endswith("docs/core/index.html")
    assert cw.resolve_clean_url("/assets/css/theme.css").name == "theme.css"
    assert cw.resolve_clean_url("/no-such-page") is None
