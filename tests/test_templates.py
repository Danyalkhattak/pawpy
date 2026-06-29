"""Tests for template expansion."""

from pawpy.mutations.templates import _resolve_token, expand_templates


def test_resolve_firstname():
    profile = {"firstname": "John"}
    result = _resolve_token("firstname", profile)
    assert "john" in result
    assert "John" in result


def test_resolve_year():
    profile = {}
    result = _resolve_token("year", profile)
    # Should contain years from ~40 years ago to current
    assert len(result) > 30


def test_resolve_digit():
    profile = {}
    result = _resolve_token("digit", profile)
    assert "0" in result
    assert "9" in result


def test_expand_simple_template():
    templates = ["[firstname][year]"]
    profile = {"firstname": "John"}
    result = expand_templates(templates, profile)
    assert len(result) > 30  # John + multiple years


def test_expand_unknown_token():
    # Unknown tokens resolve to empty lists, so cartesian product is empty
    templates = ["[unknown_token]"]
    profile = {}
    result = expand_templates(templates, profile)
    assert result == []


def test_expand_multiple_tokens():
    templates = ["[firstname][sep][lastname]"]
    profile = {"firstname": "John", "lastname": "Doe"}
    result = expand_templates(templates, profile)
    assert "john-doe" in result
    assert "john.doe" in result
    assert "John-Doe" in result
