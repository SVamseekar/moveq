"""Config and deployment contract tests for website/ (vercel.json, package.json, dev_server)."""

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_website.py"
_SPEC = importlib.util.spec_from_file_location("check_website", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
cw = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cw)

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"


def test_vercel_json_production_contract():
    path = WEBSITE / "vercel.json"
    assert path.is_file(), "website/vercel.json must exist"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("cleanUrls") is True
    assert data.get("trailingSlash") is False
    assert data.get("framework") is None
    assert "ignoreCommand" in data
    assert "git diff" in data["ignoreCommand"]
    assert cw.check_vercel_json(WEBSITE) == []


def test_package_json_production_contract():
    path = WEBSITE / "package.json"
    assert path.is_file(), "website/package.json must exist"
    data = json.loads(path.read_text(encoding="utf-8"))
    for dep_key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        assert not data.get(dep_key), f"package.json must not have {dep_key}"
    scripts = data.get("scripts", {})
    assert "build" not in scripts, "package.json must not define a build script"
    assert "install" not in scripts, "package.json must not define an install script"
    assert cw.check_package_json(WEBSITE) == []


def test_package_lock_json_production_contract():
    path = WEBSITE / "package-lock.json"
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        packages = data.get("packages", {})
        # Only root package entry allowed
        assert set(packages.keys()) <= {""}


def test_dev_server_import_safety():
    server_path = WEBSITE / "dev_server.py"
    assert server_path.is_file()
    spec = importlib.util.spec_from_file_location("dev_server_test_import", server_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    # Pytest runs with sys.argv containing pytest arguments like -v; importing dev_server must not crash
    spec.loader.exec_module(mod)
    assert hasattr(mod, "CleanURLHandler")
    assert hasattr(mod, "PORT")


# --- Negative / Fault Injection Tests on tmp_path fixtures ---


def test_vercel_json_missing_fails(tmp_path: Path):
    errors = cw.check_vercel_json(tmp_path)
    assert len(errors) == 1
    assert "missing" in errors[0]


@pytest.mark.parametrize(
    "config_patch,expected_err",
    [
        ({"cleanUrls": False, "trailingSlash": False, "ignoreCommand": "echo 1"}, "cleanUrls to true"),
        ({"cleanUrls": True, "trailingSlash": True, "ignoreCommand": "echo 1"}, "trailingSlash to false"),
        ({"cleanUrls": True, "trailingSlash": False, "framework": "nextjs", "ignoreCommand": "echo 1"}, "Node framework"),
        ({"cleanUrls": True, "trailingSlash": False}, "ignoreCommand"),
    ],
)
def test_vercel_json_invalid_settings_fail(tmp_path: Path, config_patch: dict, expected_err: str):
    (tmp_path / "vercel.json").write_text(json.dumps(config_patch), encoding="utf-8")
    errors = cw.check_vercel_json(tmp_path)
    assert any(expected_err in err for err in errors), f"Expected '{expected_err}' in {errors}"


def test_package_json_missing_fails(tmp_path: Path):
    errors = cw.check_package_json(tmp_path)
    assert len(errors) == 1
    assert "missing" in errors[0]


@pytest.mark.parametrize(
    "pkg_patch,expected_err",
    [
        ({"name": "site", "dependencies": {"express": "^4.18.0"}}, "dependencies must be empty"),
        ({"name": "site", "devDependencies": {"vite": "^5.0.0"}}, "devDependencies must be empty"),
        ({"name": "site", "peerDependencies": {"react": "^18.0.0"}}, "peerDependencies must be empty"),
        ({"name": "site", "optionalDependencies": {"fsevents": "^2.3.2"}}, "optionalDependencies must be empty"),
        ({"name": "site", "scripts": {"build": "next build"}}, "must not define build or install scripts"),
        ({"name": "site", "scripts": {"install": "npm install"}}, "must not define build or install scripts"),
    ],
)
def test_package_json_invalid_settings_fail(tmp_path: Path, pkg_patch: dict, expected_err: str):
    (tmp_path / "package.json").write_text(json.dumps(pkg_patch), encoding="utf-8")
    errors = cw.check_package_json(tmp_path)
    assert any(expected_err in err for err in errors), f"Expected '{expected_err}' in {errors}"

