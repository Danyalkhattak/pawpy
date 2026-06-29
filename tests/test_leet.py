"""Tests for leet-speak mutations."""

from pawpy.mutations.leet import leet_speak


def test_leet_basic_includes_original():
    result = leet_speak("admin", level=1)
    assert "admin" in result


def test_leet_level1_substitutions():
    result = leet_speak("aeios", level=1)
    assert "@3i0$" in result


def test_leet_level2_more_variants():
    r1 = leet_speak("password", level=1)
    r2 = leet_speak("password", level=2)
    assert len(r2) >= len(r1)


def test_leet_empty_string():
    result = leet_speak("", level=2)
    assert result == [""]


def test_leet_no_substitutable_chars():
    result = leet_speak("xyz", level=2)
    assert "xyz" in result


def test_leet_returns_sorted_unique():
    result = leet_speak("test", level=2)
    assert result == sorted(set(result))
