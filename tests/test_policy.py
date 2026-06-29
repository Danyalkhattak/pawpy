"""Tests for password policy filter."""

from pawpy.filters.policy import PolicyFilter


def test_min_length():
    pf = PolicyFilter(min_length=8)
    assert pf.check("abcdefgh") is True
    assert pf.check("abc") is False


def test_require_upper():
    pf = PolicyFilter(require_upper=True)
    assert pf.check("Password") is True
    assert pf.check("password") is False


def test_require_lower():
    pf = PolicyFilter(require_lower=True)
    assert pf.check("PASSWORDa") is True
    assert pf.check("PASSWORD") is False


def test_require_digit():
    pf = PolicyFilter(require_digit=True)
    assert pf.check("pass1") is True
    assert pf.check("password") is False


def test_require_special():
    pf = PolicyFilter(require_special=True)
    assert pf.check("pass!") is True
    assert pf.check("password") is False


def test_combined_policy():
    pf = PolicyFilter(min_length=8, require_upper=True, require_digit=True)
    assert pf.check("Password1") is True
    assert pf.check("password1") is False  # no upper
    assert pf.check("Password") is False  # no digit
    assert pf.check("Pass1") is False  # too short


def test_no_filters():
    pf = PolicyFilter()
    assert pf.check("") is True
    assert pf.check("anything") is True
