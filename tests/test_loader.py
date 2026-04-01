import json
import yaml
import pytest

from aidecl.loader import load_file, load_schema


def test_load_json(tmp_path):
    p = tmp_path / "test.json"
    p.write_text(json.dumps({"key": "val"}))
    data, fmt, err = load_file(str(p))
    assert err is None
    assert fmt == "json"
    assert data["key"] == "val"


def test_load_yaml(tmp_path):
    p = tmp_path / "test.yaml"
    p.write_text("key: val\n")
    data, fmt, err = load_file(str(p))
    assert err is None
    assert fmt == "yaml"
    assert data["key"] == "val"


def test_load_yml_extension(tmp_path):
    p = tmp_path / "test.yml"
    p.write_text("key: val\n")
    data, fmt, err = load_file(str(p))
    assert err is None
    assert fmt == "yaml"


def test_unknown_extension_json(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text(json.dumps({"key": "val"}))
    data, fmt, err = load_file(str(p))
    assert err is None
    assert fmt == "json"


def test_unknown_extension_yaml(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("key: val\n")
    data, fmt, err = load_file(str(p))
    assert err is None
    assert fmt == "yaml"


def test_missing_file():
    data, fmt, err = load_file("/nonexistent/path.yaml")
    assert data is None
    assert "not found" in err


def test_empty_file(tmp_path):
    p = tmp_path / "empty.yaml"
    p.write_text("")
    data, fmt, err = load_file(str(p))
    assert data is None
    assert err is not None


def test_binary_file(tmp_path):
    p = tmp_path / "binary.yaml"
    p.write_bytes(b"\x00\x01\x02\xff\xfe")
    data, fmt, err = load_file(str(p))
    assert data is None
    assert "binary" in err or "UTF-8" in err


def test_load_schema():
    schema, err = load_schema()
    assert err is None
    assert schema is not None
    assert "$schema" in schema


def test_load_schema_verbose():
    schema, err = load_schema(verbose=True)
    assert err is None
    assert schema is not None
