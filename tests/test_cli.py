import json
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def run_cli(*args):
    result = subprocess.run(
        [sys.executable, "-m", "aidecl_validate"] + list(args),
        capture_output=True, text=True, timeout=30,
    )
    return result


def test_valid_file():
    r = run_cli("validate", str(FIXTURES / "valid.yaml"))
    assert r.returncode == 0
    assert "PASS" in r.stdout


def test_invalid_file():
    r = run_cli("validate", str(FIXTURES / "invalid.yaml"))
    assert r.returncode == 2
    assert "FAIL" in r.stdout


def test_nonexistent_file():
    r = run_cli("validate", "/tmp/does_not_exist_xyz.yaml")
    assert r.returncode != 0


def test_semantic_warning():
    r = run_cli("validate", "--verbose", str(FIXTURES / "semantic-warning.yaml"))
    # should pass (warnings are not errors by default)
    assert r.returncode == 0


def test_strict_mode():
    r = run_cli("--strict", "validate", str(FIXTURES / "semantic-warning.yaml"))
    assert r.returncode == 1


def test_json_output():
    r = run_cli("validate", "-f", "json", str(FIXTURES / "valid.yaml"))
    assert r.returncode == 0
    parsed = json.loads(r.stdout)
    assert parsed["passed"] is True


def test_github_actions_output():
    r = run_cli("validate", "-f", "github-actions", str(FIXTURES / "invalid.yaml"))
    assert "::error" in r.stdout


def test_quiet_mode():
    r = run_cli("--quiet", "validate", str(FIXTURES / "valid.yaml"))
    assert r.returncode == 0
    assert r.stdout.strip() == ""


def test_version():
    r = run_cli("--version")
    assert r.returncode == 0
    assert "aidecl-validate" in r.stdout


def test_no_color():
    r = run_cli("--no-color", "validate", str(FIXTURES / "valid.yaml"))
    assert r.returncode == 0
    assert "\033[" not in r.stdout
