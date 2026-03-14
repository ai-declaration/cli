import json
import pytest
import yaml

from aidecl_validate.loader import load_schema


@pytest.fixture(scope="session")
def schema():
    s, err = load_schema()
    assert err is None, f"Failed to load schema: {err}"
    return s


@pytest.fixture
def valid_data():
    return {
        "schema_version": "1.0.0",
        "project": {"name": "test-project"},
        "ai_usage": {"used": False},
        "declaration": {
            "date": "2025-01-15",
            "declared_by": "Test Team",
        },
    }


@pytest.fixture
def valid_ai_data():
    return {
        "schema_version": "1.0.0",
        "project": {"name": "test-project"},
        "ai_usage": {
            "used": True,
            "summary": "Used for testing",
            "level": "minimal",
            "tools": [
                {"name": "TestTool", "type": "assistant"}
            ],
        },
        "declaration": {
            "date": "2025-01-15",
            "declared_by": "Test Team",
        },
    }


def make_file(tmp_path, data, fmt="yaml"):
    if fmt == "yaml":
        p = tmp_path / "test.yaml"
        p.write_text(yaml.dump(data, default_flow_style=False))
    else:
        p = tmp_path / "test.json"
        p.write_text(json.dumps(data, indent=2))
    return str(p)
