#!/usr/bin/env python3
"""Static-site checks for website/ (Vercel, no Node build).

Usage:
    python scripts/check_website.py

Exit 0 if clean-URL pages, assets, vercel.json, package.json, and HTML/JS
contracts match the deploy contract. Does not bump package versions.
"""

from __future__ import annotations

import html.parser
import json
import os
import sys
import threading
import urllib.parse
from http.client import HTTPConnection
from http.server import HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"

REQUIRED_ROUTES: tuple[str, ...] = (
    "/",
    "/docs",
    "/docs/core",
    "/docs/scoring",
    "/docs/catalogue",
    "/docs/frames",
    "/docs/cli",
    "/guides",
    "/playground",
    "/reference",
    "/blog",
    "/assets/css/theme.css",
    "/assets/js/version.js",
    "/assets/js/theme.js",
    "/assets/images/favicon.svg",
)

EXPECTED_CONTENT_TYPES: dict[str, tuple[str, ...]] = {
    ".html": ("text/html",),
    ".css": ("text/css",),
    ".js": ("application/javascript", "text/javascript"),
    ".svg": ("image/svg+xml",),
}

_DEP_KEYS = (
    "dependencies",
    "devDependencies",
    "optionalDependencies",
    "peerDependencies",
)


def resolve_clean_url(url_path: str, root: Path = WEBSITE) -> Path | None:
    """Map a clean URL to a file under *root*, or None if missing."""
    path = url_path.split("?")[0].split("#")[0]
    if not path.startswith("/"):
        return None
    rel = path.lstrip("/")
    if path in ("", "/"):
        candidate = root / "index.html"
        return candidate if candidate.is_file() else None
    exact = root / rel
    if exact.is_file():
        return exact
    as_index = exact / "index.html"
    if as_index.is_file():
        return as_index
    as_html = root / (rel + ".html")
    if as_html.is_file():
        return as_html
    return None


def check_vercel_json(root: Path = WEBSITE) -> list[str]:
    path = root / "vercel.json"
    errors: list[str] = []
    if not path.is_file():
        return [f"missing {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"invalid JSON in {path.name}: {e}"]

    if data.get("cleanUrls") is not True:
        errors.append(f"{path.name} must set cleanUrls to true")
    if data.get("trailingSlash") is not False:
        errors.append(f"{path.name} must set trailingSlash to false")
    if data.get("framework") not in (None,):
        errors.append(f"{path.name} must not set a Node framework")
    if not data.get("ignoreCommand"):
        errors.append(f"{path.name} must declare an ignoreCommand")
    return errors


def check_package_json(root: Path = WEBSITE) -> list[str]:
    path = root / "package.json"
    errors: list[str] = []
    if not path.is_file():
        return [f"missing {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"invalid JSON in {path.name}: {e}"]

    for key in _DEP_KEYS:
        deps = data.get(key) or {}
        if deps:
            errors.append(f"{path.name} {key} must be empty (no Node build)")
    scripts = data.get("scripts") or {}
    if "build" in scripts or "install" in scripts:
        errors.append(f"{path.name} must not define build or install scripts")

    # If package-lock.json exists, ensure dependencies is empty
    lock_path = root / "package-lock.json"
    if lock_path.is_file():
        try:
            lock_data = json.loads(lock_path.read_text(encoding="utf-8"))
            if lock_data.get("dependencies"):
                errors.append(f"{lock_path.name} must not contain third-party dependencies")
        except Exception as e:
            errors.append(f"invalid JSON in {lock_path.name}: {e}")

    return errors


def check_required_routes(root: Path = WEBSITE) -> list[str]:
    errors: list[str] = []
    for route in REQUIRED_ROUTES:
        if resolve_clean_url(route, root) is None:
            errors.append(f"missing file for clean URL {route}")
    return errors


class HtmlPageData(html.parser.HTMLParser):
    """Parses an HTML file extracting IDs, links, scripts, stylesheets, and accessibility."""

    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.srcs: list[str] = []
        self.scripts: list[str] = []
        self.nav_hrefs: set[str] = set()
        self.in_nav: bool = False
        self.html_attrs: dict[str, str | None] = {}
        self.has_html: bool = False
        self.head_count: int = 0
        self.body_count: int = 0
        self.meta_viewport: bool = False
        self.has_favicon: bool = False
        self.has_theme_css: bool = False
        self.has_theme_toggle_btn: bool = False
        self.theme_toggle_has_accessible_name: bool = False
        self.empty_attributes: list[str] = []
        self.imgs_missing_alt: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)

        if tag == "html":
            self.has_html = True
            self.html_attrs = attrs_dict
        elif tag == "head":
            self.head_count += 1
        elif tag == "body":
            self.body_count += 1
        elif tag == "nav":
            self.in_nav = True

        element_id = attrs_dict.get("id")
        if element_id:
            self.ids.add(element_id)
            if element_id == "themeToggleBtn":
                self.has_theme_toggle_btn = True
                if attrs_dict.get("aria-label") or attrs_dict.get("title"):
                    self.theme_toggle_has_accessible_name = True

        if tag == "meta" and attrs_dict.get("name") == "viewport":
            self.meta_viewport = True

        if tag == "link":
            rel = attrs_dict.get("rel", "")
            href = attrs_dict.get("href", "")
            if "icon" in rel and "favicon" in href:
                self.has_favicon = True
            if "stylesheet" in rel and "theme.css" in href:
                self.has_theme_css = True

        if tag == "script" and "src" in attrs_dict:
            src_val = attrs_dict["src"]
            if src_val:
                self.scripts.append(src_val)

        if "href" in attrs_dict:
            href_val = attrs_dict["href"]
            if href_val is not None:
                if href_val.strip() == "":
                    self.empty_attributes.append(f"empty href in <{tag}>")
                else:
                    self.hrefs.append(href_val)
                    if self.in_nav:
                        self.nav_hrefs.add(href_val)

        if "src" in attrs_dict:
            src_val = attrs_dict["src"]
            if src_val is not None:
                if src_val.strip() == "":
                    self.empty_attributes.append(f"empty src in <{tag}>")
                else:
                    self.srcs.append(src_val)

        if tag == "img":
            alt = attrs_dict.get("alt")
            aria_hidden = attrs_dict.get("aria-hidden")
            aria_label = attrs_dict.get("aria-label")
            if alt is None and aria_label is None and aria_hidden != "true":
                self.imgs_missing_alt.append(f"<img src='{attrs_dict.get('src', '')}'> missing alt")

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav":
            self.in_nav = False


def parse_all_pages(root: Path = WEBSITE) -> dict[str, HtmlPageData]:
    """Parse all .html files under *root* returning relative path to parsed data."""
    pages: dict[str, HtmlPageData] = {}
    for html_file in sorted(root.rglob("*.html")):
        parser = HtmlPageData()
        parser.feed(html_file.read_text(encoding="utf-8"))
        pages[html_file.relative_to(root).as_posix()] = parser
    return pages


def internal_refs(root: Path = WEBSITE) -> list[tuple[Path, str]]:
    """Return all root-relative internal references (file_path, url)."""
    found: list[tuple[Path, str]] = []
    pages = parse_all_pages(root)
    for rel_str, page_data in pages.items():
        file_path = root / rel_str
        for ref in page_data.hrefs + page_data.srcs:
            if ref.startswith("/"):
                found.append((file_path, ref))
    return found


def check_internal_refs(root: Path = WEBSITE) -> list[str]:
    """Validate that every internal link, asset, and anchor fragment resolves."""
    errors: list[str] = []
    pages = parse_all_pages(root)

    for rel_str, page_data in pages.items():
        # Check in-page anchors
        for href in page_data.hrefs:
            if href.startswith("#"):
                anchor = href[1:]
                if anchor and anchor not in page_data.ids:
                    errors.append(f"{rel_str}: broken in-page anchor #{anchor}")
            elif href.startswith("/"):
                parsed = urllib.parse.urlparse(href)
                target_file = resolve_clean_url(parsed.path, root)
                if target_file is None:
                    errors.append(f"{rel_str}: broken internal link {href}")
                elif parsed.fragment:
                    target_rel = target_file.relative_to(root).as_posix()
                    if target_rel in pages:
                        if parsed.fragment not in pages[target_rel].ids:
                            errors.append(
                                f"{rel_str}: broken cross-page anchor {href} (#{parsed.fragment} not in {target_rel})"
                            )

        # Check asset sources
        for src in page_data.srcs:
            if src.startswith("/"):
                parsed = urllib.parse.urlparse(src)
                if resolve_clean_url(parsed.path, root) is None:
                    errors.append(f"{rel_str}: broken asset source {src}")

    return errors


def check_html_structure(root: Path = WEBSITE) -> list[str]:
    """Validate HTML tag structure, metadata, favicon, theme toggle, and accessibility."""
    errors: list[str] = []
    pages = parse_all_pages(root)
    required_nav = {"/docs", "/guides", "/reference", "/playground", "/blog"}

    for rel_str, page in pages.items():
        if not page.has_html:
            errors.append(f"{rel_str}: missing <html> tag")
        elif page.html_attrs.get("lang") != "en":
            errors.append(f"{rel_str}: <html> missing lang='en'")

        if not page.html_attrs.get("data-theme"):
            errors.append(f"{rel_str}: <html> missing data-theme attribute")

        if page.head_count != 1:
            errors.append(f"{rel_str}: expected exactly 1 <head>, found {page.head_count}")
        if page.body_count != 1:
            errors.append(f"{rel_str}: expected exactly 1 <body>, found {page.body_count}")

        if not page.meta_viewport:
            errors.append(f"{rel_str}: missing <meta name='viewport'> tag")
        if not page.has_favicon:
            errors.append(f"{rel_str}: missing favicon link /assets/images/favicon.svg")
        if not page.has_theme_css:
            errors.append(f"{rel_str}: missing stylesheet link /assets/css/theme.css")

        if not page.has_theme_toggle_btn:
            errors.append(f"{rel_str}: missing #themeToggleBtn element")
        elif not page.theme_toggle_has_accessible_name:
            errors.append(f"{rel_str}: #themeToggleBtn missing accessible name (aria-label)")

        missing_nav = required_nav - page.nav_hrefs
        if missing_nav:
            errors.append(f"{rel_str}: navigation missing links to {sorted(missing_nav)}")

        for empty_attr in page.empty_attributes:
            errors.append(f"{rel_str}: {empty_attr}")
        for missing_alt in page.imgs_missing_alt:
            errors.append(f"{rel_str}: {missing_alt}")

    return errors


def check_js_html_coupling(root: Path = WEBSITE) -> list[str]:
    """Ensure element IDs required by JS exist on pages where the scripts are loaded."""
    errors: list[str] = []
    pages = parse_all_pages(root)

    for rel_str, page in pages.items():
        for script_src in page.scripts:
            script_name = script_src.split("?")[0].split("/")[-1]
            if script_name == "theme.js":
                if "themeToggleBtn" not in page.ids:
                    errors.append(f"{rel_str} loads theme.js but lacks #themeToggleBtn")
            elif script_name == "search.js":
                for required_id in ("searchModal", "searchInput", "searchResults"):
                    if required_id not in page.ids:
                        errors.append(f"{rel_str} loads search.js but lacks #{required_id}")
            elif script_name == "playground.js":
                if "lorenzCanvas" not in page.ids:
                    errors.append(f"{rel_str} loads playground.js but lacks #lorenzCanvas")
            elif script_name == "terminal.js":
                for required_id in ("terminalCmd", "terminalOutput"):
                    if required_id not in page.ids:
                        errors.append(f"{rel_str} loads terminal.js but lacks #{required_id}")
            elif script_name == "benchmarks.js":
                for required_id in ("benchTitle", "benchSubtitle", "benchFootnote", "benchBars"):
                    if required_id not in page.ids:
                        errors.append(f"{rel_str} loads benchmarks.js but lacks #{required_id}")

    return errors


def _load_handler(root: Path = WEBSITE):
    import importlib.util

    script = root / "dev_server.py" if (root / "dev_server.py").is_file() else WEBSITE / "dev_server.py"
    spec = importlib.util.spec_from_file_location("moveq_website_dev_server", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CleanURLHandler


def check_http_routes(root: Path = WEBSITE) -> list[str]:
    """Test HTTP responses against CleanURLHandler for required routes and 404s."""
    errors: list[str] = []
    base = _load_handler(root)

    doc_dir = str(root)

    class QuietHandler(base):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=doc_dir, **kwargs)

        def log_message(self, format, *args):
            return

    server = HTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    try:
        for route in REQUIRED_ROUTES:
            conn = HTTPConnection(host, port, timeout=5)
            conn.request("GET", route)
            response = conn.getresponse()
            status = response.status
            content_type = response.getheader("Content-Type", "")
            body = response.read()
            conn.close()

            if status != 200:
                errors.append(f"GET {route} returned {status}")
                continue

            if not body:
                errors.append(f"GET {route} returned empty body")

            # Validate Content-Type
            target_file = resolve_clean_url(route, root)
            if target_file is not None:
                expected_prefixes = EXPECTED_CONTENT_TYPES.get(target_file.suffix, ())
                if expected_prefixes and not any(prefix in content_type for prefix in expected_prefixes):
                    errors.append(
                        f"GET {route} Content-Type '{content_type}' does not match expected {expected_prefixes}"
                    )

        # Negative test for 404
        conn = HTTPConnection(host, port, timeout=5)
        conn.request("GET", "/nonexistent-page-check-404")
        response = conn.getresponse()
        if response.status != 404:
            errors.append(f"GET /nonexistent-page-check-404 returned {response.status}, expected 404")
        response.read()
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
    return errors


def collect_errors(root: Path = WEBSITE) -> list[str]:
    errors: list[str] = []
    errors.extend(check_vercel_json(root))
    errors.extend(check_package_json(root))
    errors.extend(check_required_routes(root))
    errors.extend(check_internal_refs(root))
    errors.extend(check_html_structure(root))
    errors.extend(check_js_html_coupling(root))
    errors.extend(check_http_routes(root))
    return errors


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    root = WEBSITE
    if argv and not argv[0].startswith("-"):
        root = Path(argv[0]).resolve()

    errors = collect_errors(root)
    if errors:
        print("website checks failed:", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1
    print("Website clean-URL routes, assets, HTML structure, and Vercel config are ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
