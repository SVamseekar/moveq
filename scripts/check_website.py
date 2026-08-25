#!/usr/bin/env python3
"""Static-site checks for website/ (Vercel, no Node build).

Usage:
    python scripts/check_website.py

Exit 0 if clean-URL pages, assets, vercel.json, and package.json match the
deploy contract. Does not bump package versions.
"""

from __future__ import annotations

import json
import re
import sys
import threading
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

_REF_RE = re.compile(
    r"""(?:href|src)\s*=\s*["'](/[^"'#?]*)""",
    re.IGNORECASE,
)
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
        return [f"missing {path.relative_to(ROOT)}"]
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("cleanUrls") is not True:
        errors.append("website/vercel.json must set cleanUrls to true")
    if data.get("trailingSlash") is not False:
        errors.append("website/vercel.json must set trailingSlash to false")
    if data.get("framework") not in (None,):
        errors.append("website/vercel.json must not set a Node framework")
    return errors


def check_package_json(root: Path = WEBSITE) -> list[str]:
    path = root / "package.json"
    errors: list[str] = []
    if not path.is_file():
        return [f"missing {path.relative_to(ROOT)}"]
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in _DEP_KEYS:
        deps = data.get(key) or {}
        if deps:
            errors.append(f"website/package.json {key} must be empty (no Node build)")
    scripts = data.get("scripts") or {}
    if "build" in scripts or "install" in scripts:
        errors.append("website/package.json must not define build or install scripts")
    return errors


def check_required_routes(root: Path = WEBSITE) -> list[str]:
    errors: list[str] = []
    for route in REQUIRED_ROUTES:
        if resolve_clean_url(route, root) is None:
            errors.append(f"missing file for clean URL {route}")
    return errors


def internal_refs(root: Path = WEBSITE) -> list[tuple[Path, str]]:
    found: list[tuple[Path, str]] = []
    for html in sorted(root.rglob("*.html")):
        text = html.read_text(encoding="utf-8")
        for match in _REF_RE.finditer(text):
            found.append((html, match.group(1)))
    return found


def check_internal_refs(root: Path = WEBSITE) -> list[str]:
    errors: list[str] = []
    for html, url in internal_refs(root):
        if resolve_clean_url(url, root) is None:
            rel = html.relative_to(root)
            errors.append(f"{rel}: broken internal link {url}")
    return errors


def _load_handler():
    import importlib.util

    script = WEBSITE / "dev_server.py"
    spec = importlib.util.spec_from_file_location("moveq_website_dev_server", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CleanURLHandler


def check_http_routes(root: Path = WEBSITE) -> list[str]:
    del root  # handler always serves WEBSITE
    errors: list[str] = []
    base = _load_handler()

    class QuietHandler(base):
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
            response.read()
            conn.close()
            if status != 200:
                errors.append(f"GET {route} returned {status}")
    finally:
        server.shutdown()
        server.server_close()
    return errors


def collect_errors() -> list[str]:
    errors: list[str] = []
    errors.extend(check_vercel_json())
    errors.extend(check_package_json())
    errors.extend(check_required_routes())
    errors.extend(check_internal_refs())
    errors.extend(check_http_routes())
    return errors


def main() -> int:
    errors = collect_errors()
    if errors:
        print("website checks failed:", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1
    print("Website clean-URL routes, assets, and Vercel config are ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
