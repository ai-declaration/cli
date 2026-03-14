import pytest
from datetime import date, timedelta

from aidecl_validate.semantic import validate_semantics


def _base():
    return {
        "schema_version": "1.0.0",
        "project": {"name": "test"},
        "ai_usage": {"used": False},
        "declaration": {"date": "2025-01-15", "declared_by": "Team"},
    }


def test_rule1_used_no_tools():
    d = _base()
    d["ai_usage"] = {"used": True, "summary": "test", "tools": []}
    warns, errs = validate_semantics(d)
    assert any("no tools" in w for w in warns)


def test_rule2_not_used_with_tools():
    d = _base()
    d["ai_usage"] = {"used": False, "tools": [{"name": "X"}]}
    warns, errs = validate_semantics(d)
    assert any("used is false but tools" in e for e in errs)


def test_rule3_not_used_wrong_level():
    d = _base()
    d["ai_usage"] = {"used": False, "level": "significant"}
    warns, errs = validate_semantics(d)
    assert any("level" in e for e in errs)


def test_rule4_proportion_sum():
    d = _base()
    d["ai_usage"]["code_proportion"] = {
        "ai_generated_percent": 50,
        "ai_assisted_percent": 60,
        "human_only_percent": 10,
    }
    warns, _ = validate_semantics(d)
    assert any("sum to 120" in w for w in warns)


def test_rule4_all_zeros_no_warning():
    d = _base()
    d["ai_usage"]["code_proportion"] = {
        "ai_generated_percent": 0,
        "ai_assisted_percent": 0,
        "human_only_percent": 0,
    }
    warns, _ = validate_semantics(d)
    assert not any("sum" in w for w in warns)


def test_rule5_future_date():
    d = _base()
    future = (date.today() + timedelta(days=30)).isoformat()
    d["declaration"]["date"] = future
    warns, _ = validate_semantics(d)
    assert any("future" in w for w in warns)


def test_rule6_review_after_declaration():
    d = _base()
    d["declaration"]["date"] = "2025-01-01"
    d["declaration"]["review_date"] = "2025-02-01"
    warns, _ = validate_semantics(d)
    assert any("review_date" in w for w in warns)


def test_rule7_review_no_type():
    d = _base()
    d["security"] = {"review_performed": True}
    warns, _ = validate_semantics(d)
    assert any("review_type" in w for w in warns)


def test_rule8_personal_data_no_dpa():
    d = _base()
    d["data_handling"] = {"personal_data_sent": True}
    warns, _ = validate_semantics(d)
    assert any("DPA" in w for w in warns)


def test_rule9_extensive_no_proportion():
    d = _base()
    d["ai_usage"] = {"used": True, "summary": "x", "level": "extensive"}
    warns, _ = validate_semantics(d)
    assert any("extensive" in w for w in warns)


def test_rule10_component_tool_not_listed():
    d = _base()
    d["ai_usage"] = {
        "used": True,
        "summary": "x",
        "tools": [{"name": "ToolA"}],
        "components": [
            {"name": "Comp1", "tools_used": ["ToolB"]}
        ],
    }
    warns, _ = validate_semantics(d)
    assert any("ToolB" in w for w in warns)


def test_rule11_newer_schema():
    d = _base()
    d["schema_version"] = "2.0.0"
    warns, _ = validate_semantics(d)
    assert any("newer" in w for w in warns)


def test_rule12_inverted_period():
    d = _base()
    d["ai_usage"] = {
        "used": True,
        "summary": "x",
        "tools": [{"name": "T", "period": {"start": "2025-06-01", "end": "2025-01-01"}}],
    }
    _, errs = validate_semantics(d)
    assert any("before start" in e for e in errs)


def test_rule13_trains_no_data_handling():
    d = _base()
    d["ai_usage"] = {
        "used": True,
        "summary": "x",
        "tools": [{"name": "T", "trains_on_data": True}],
    }
    warns, _ = validate_semantics(d)
    assert any("trains on data" in w for w in warns)


def test_rule14_past_next_review():
    d = _base()
    past = (date.today() - timedelta(days=30)).isoformat()
    d["declaration"]["next_review"] = past
    warns, _ = validate_semantics(d)
    assert any("overdue" in w for w in warns)


def test_clean_data_no_warnings():
    d = _base()
    warns, errs = validate_semantics(d)
    assert warns == []
    assert errs == []
