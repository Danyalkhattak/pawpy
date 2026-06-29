"""Tests for hybrid mask attack generation."""

from pawpy.generator.hybrid import _expand_mask, _parse_mask, hybrid_generate


def test_parse_mask_lowercase():
    result = _parse_mask("?l?l")
    assert len(result) == 2
    # _parse_mask returns char sets as strings (iterable), not lists
    assert "abcdefghijklmnopqrstuvwxyz" in result[0]  # result[0] is a string


def test_parse_mask_digits():
    result = _parse_mask("?d?d?d")
    assert len(result) == 3
    assert all(c in "0123456789" for c in result[0])


def test_parse_mask_mixed():
    result = _parse_mask("?l?d!")
    assert len(result) == 3


def test_hybrid_right_mask():
    words = ["pass", "word"]
    result = hybrid_generate(words, right_mask="?d?d")
    assert "pass00" in result
    assert "word00" in result
    assert "pass99" in result


def test_hybrid_left_mask():
    words = ["admin"]
    result = hybrid_generate(words, left_mask="?u?u")
    assert "AAadmin" in result
    assert "ZZadmin" in result


def test_hybrid_no_mask():
    words = ["test"]
    result = hybrid_generate(words)
    assert result == []


def test_expand_mask_capped():
    # Very large mask should be capped
    parts = [list("abcdefghijklmnopqrstuvwxyz")] * 4
    result = _expand_mask(parts, max_results=100)
    assert len(result) <= 100
