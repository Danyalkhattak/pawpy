"""Tests for date permutations."""

from pawpy.mutations.dates import date_permutations


def test_valid_date():
    result = date_permutations("01011990")
    assert "01" in result
    assert "1990" in result
    assert "90" in result
    assert "01011990" in result


def test_invalid_date():
    result = date_permutations("notadate")
    assert result == []


def test_empty_date():
    result = date_permutations("")
    assert result == []


def test_date_contains_variants():
    result = date_permutations("31122000")
    assert "31" in result
    assert "12" in result
    assert "2000" in result
    assert "00" in result
    assert "3112" in result
    assert "1231" in result


def test_date_deduplicated():
    result = date_permutations("01011990")
    assert result == list(dict.fromkeys(result))  # preserves order, unique
