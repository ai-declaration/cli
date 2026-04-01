import pytest

from aidecl.schema import validate_schema


def test_valid_data(schema, valid_data):
    errs = validate_schema(valid_data, schema)
    assert errs == []


def test_valid_ai_data(schema, valid_ai_data):
    errs = validate_schema(valid_ai_data, schema)
    assert errs == []


def test_missing_schema_version(schema, valid_data):
    del valid_data["schema_version"]
    errs = validate_schema(valid_data, schema)
    assert len(errs) > 0
    assert any("schema_version" in e for e in errs)


def test_missing_project(schema, valid_data):
    del valid_data["project"]
    errs = validate_schema(valid_data, schema)
    assert len(errs) > 0


def test_invalid_level(schema, valid_ai_data):
    valid_ai_data["ai_usage"]["level"] = "high"
    errs = validate_schema(valid_ai_data, schema)
    assert len(errs) > 0
    assert any("level" in e for e in errs)


def test_conditional_summary_required(schema):
    data = {
        "schema_version": "1.0.0",
        "project": {"name": "test"},
        "ai_usage": {"used": True},
        "declaration": {"date": "2025-01-01", "declared_by": "Team"},
    }
    errs = validate_schema(data, schema)
    assert any("summary" in e for e in errs)


def test_percentage_bounds(schema, valid_ai_data):
    valid_ai_data["ai_usage"]["code_proportion"] = {
        "ai_generated_percent": 150
    }
    errs = validate_schema(valid_ai_data, schema)
    assert len(errs) > 0


def test_verbose_mode(schema, valid_data):
    # should not crash in verbose mode
    errs = validate_schema(valid_data, schema, verbose=True)
    assert errs == []
