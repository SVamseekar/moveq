import html.parser
import importlib.util
import threading
from http.client import HTTPConnection
from http.server import HTTPServer
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_website.py"
_SPEC = importlib.util.spec_from_file_location("check_website", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
cw = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cw)

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"

# Independent table of routes, expected Content-Type substrings, and body snippets
INDEPENDENT_PAGE_SNIPPETS: dict[str, dict[str, str]] = {
    "/": {
        "title": "moveq — Fast, Auditable Transport-Equity Toolkit",
        "h1": "fast transport-equity toolkit",
    },
    "/docs": {
        "title": "Documentation Overview | moveq",
        "h1": "Introduction to moveq",
    },
    "/docs/core": {
        "title": "Core Inequality Engine | moveq Docs",
        "h1": "Core Inequality Engine",
    },
    "/docs/scoring": {
        "title": "Composite Scoring Engine | moveq Docs",
        "h1": "Composite Accessibility Scoring",
    },
    "/docs/catalogue": {
        "title": "Harmonization Registry | moveq Docs",
        "h1": "Cross-Country Harmonization Registry",
    },
    "/docs/frames": {
        "title": "DataFrame & Vulnerability Helpers | moveq Docs",
        "h1": "DataFrame & Vulnerability Helpers",
    },
    "/docs/cli": {
        "title": "CLI Command Reference | moveq Docs",
        "h1": "Command-Line Interface Reference",
    },
    "/guides": {
        "title": "Guides & Recipes | moveq",
        "h1": "Practical Guides",
    },
    "/playground": {
        "title": "Interactive Equity Playground | moveq",
        "h1": "Lorenz Curve & Inequality Playground",
    },
    "/reference": {
        "title": "API Reference | moveq",
        "h1": "Exhaustive API Index",
    },
    "/blog": {
        "title": "Briefings & Changelog | moveq",
        "h1": "Methodology & Releases",
    },
}

INDEPENDENT_ASSET_SNIPPETS: dict[str, dict[str, str | tuple[str, ...]]] = {
    "/assets/css/theme.css": {
        "mime": ("text/css",),
        "snippet": "--accent-metro",
    },
    "/assets/js/version.js": {
        "mime": ("application/javascript", "text/javascript"),
        "snippet": "SVamseekar/moveq",
    },
    "/assets/js/theme.js": {
        "mime": ("application/javascript", "text/javascript"),
        "snippet": "moveq-theme",
    },
    "/assets/images/favicon.svg": {
        "mime": ("image/svg+xml",),
        "snippet": "<svg",
    },
}


@pytest.fixture(scope="module")
def http_server():
    """Spin up a CleanURLHandler HTTP server on ephemeral port 0 with quiet logging."""
    server_path = WEBSITE / "dev_server.py"
    spec = importlib.util.spec_from_file_location("test_http_dev_server", server_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    handler_class = mod.CleanURLHandler

    class QuietHandler(handler_class):
        def log_message(self, format, *args):
            return

    server = HTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    yield host, port
    server.shutdown()
    server.server_close()


class H1Extractor(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_h1 = False
        self.h1_text = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "h1":
            self.in_h1 = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1":
            self.in_h1 = False

    def handle_data(self, data: str) -> None:
        if self.in_h1:
            self.h1_text += data


@pytest.mark.parametrize("route,expected", list(INDEPENDENT_PAGE_SNIPPETS.items()))
def test_html_routes_http_200_and_content(http_server, route: str, expected: dict[str, str]):
    host, port = http_server
    conn = HTTPConnection(host, port, timeout=5)
    conn.request("GET", route)
    res = conn.getresponse()
    body = res.read().decode("utf-8")
    content_type = res.getheader("Content-Type", "")
    content_length = res.getheader("Content-Length")
    conn.close()

    assert res.status == 200, f"Expected 200 for {route}, got {res.status}"
    assert "text/html" in content_type
    assert content_length is not None
    assert int(content_length) == len(body.encode("utf-8"))

    # Assert real title and h1 strings from the page
    assert f"<title>{expected['title']}</title>" in body, f"Missing expected title in {route}"

    extractor = H1Extractor()
    extractor.feed(body)
    clean_h1 = " ".join(extractor.h1_text.split()).lower()
    assert expected["h1"].lower() in clean_h1, f"Missing expected h1 snippet '{expected['h1']}' in {route} (got '{clean_h1}')"


@pytest.mark.parametrize("route,expected", list(INDEPENDENT_ASSET_SNIPPETS.items()))
def test_asset_routes_http_200_and_content(http_server, route: str, expected: dict[str, str | tuple[str, ...]]):
    host, port = http_server
    conn = HTTPConnection(host, port, timeout=5)
    conn.request("GET", route)
    res = conn.getresponse()
    body = res.read().decode("utf-8", errors="replace")
    content_type = res.getheader("Content-Type", "")
    conn.close()

    assert res.status == 200, f"Expected 200 for {route}, got {res.status}"
    assert any(mime in content_type for mime in expected["mime"]), (
        f"Content-Type '{content_type}' did not match {expected['mime']} for {route}"
    )
    assert str(expected["snippet"]) in body, f"Snippet '{expected['snippet']}' not found in {route}"


def test_unknown_path_returns_404(http_server):
    host, port = http_server
    conn = HTTPConnection(host, port, timeout=5)
    conn.request("GET", "/nonexistent-slug-xyz")
    res = conn.getresponse()
    res.read()
    conn.close()
    assert res.status == 404, f"Expected 404 for unknown route, got {res.status}"
