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


def test_navigation_states_transport_and_engine():
    pages = list((WEBSITE).rglob("*.html"))
    assert pages
    for path in pages:
        text = path.read_text(encoding="utf-8")
        assert 'class="identity-nav"' in text, path
        assert "Entry point and worked domain" in text, path
        assert "Any allocation, service, burden, or outcome" in text, path
        assert 'href="/guides"' in text, path
        assert 'href="/docs/core"' in text, path
    home = (WEBSITE / "index.html").read_text(encoding="utf-8")
    assert 'id="dual-identity"' in home
    assert "no separate health, energy, or household module" in home


def test_homepage_why_not_section_uses_verified_facts():
    text = (WEBSITE / "index.html").read_text(encoding="utf-8")
    assert 'id="why-not-r-or-excel"' in text
    required = (
        "Why not just use R or Excel?",
        "rineq",
        "ahead of moveq on statistical depth",
        "CI",
        "CIg",
        "CIc",
        "CIw",
        "confint.hci()",
        "sandwich",
        "decomposition()",
        "svyglm",
        "coxph",
        "mfx",
        "Nineteen summary inequality measures",
        "Health Equity Monitor",
        "HEAT Plus",
        "four variants",
        "robust standard errors",
        "survey design",
        "moveq has none of that",
        "0.250",
        "0.200",
        "not a universal error rate",
        "not a claim that",
    )
    for phrase in required:
        assert phrase in text, phrase
    lowered = text.lower()
    assert "only implementation" not in lowered
    assert "the only tool" not in lowered
    assert "rineq is wrong" not in lowered
    assert "rineq gets it wrong" not in lowered
